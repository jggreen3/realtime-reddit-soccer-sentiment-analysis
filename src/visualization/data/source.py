"""Defines a redis cache containing Reddit comment data and methods to interact with it."""

import logging
from urllib.parse import ParseResult, urlencode, urlunparse
from typing import Tuple, Union
import json
import os
import redis
import redis.exceptions
import botocore.session
from botocore.model import ServiceId
from botocore.signers import RequestSigner
from cachetools import TTLCache, cached
import pandas as pd


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ElastiCacheIAMProvider(redis.CredentialProvider):
    """Class which acts as a wrapper for elasticache IAM operations."""
    def __init__(self, user, cache_name, is_serverless=True, region="us-west-1"):
        self.user = user
        self.cache_name = cache_name
        self.is_serverless = is_serverless
        self.region = region

        session = botocore.session.get_session()
        self.request_signer = RequestSigner(
            ServiceId("elasticache"),
            self.region,
            "elasticache",
            "v4",
            session.get_credentials(),
            session.get_component("event_emitter"),
        )

    # Generated IAM tokens are valid for 15 minutes
    @cached(cache=TTLCache(maxsize=128, ttl=900))
    def get_credentials(self) -> Union[Tuple[str], Tuple[str, str]]:
        query_params = {"Action": "connect", "User": self.user}
        if self.is_serverless:
            query_params["ResourceType"] = "ServerlessCache"
        url = urlunparse(
            ParseResult(
                scheme="https",
                netloc=self.cache_name,
                path="/",
                query=urlencode(query_params),
                params="",
                fragment="",
            )
        )
        signed_url = self.request_signer.generate_presigned_url(
            {"method": "GET", "url": url, "body": {}, "headers": {}, "context": {}},
            operation_name="connect",
            expires_in=900,
            region_name=self.region,
        )
        # RequestSigner only seems to work if the URL has a protocol, but
        # Elasticache only accepts the URL without a protocol
        # So strip it off the signed URL before returning
        return (self.user, signed_url.removeprefix("https://"))



class Comment:
    """Encapsulates a Redis cache of comment data"""

    def __init__(self):
        self.redis_client = self.create_redis_client()

    def create_redis_client(self):
        """Creates a redis client using IAM credentials."""

        if os.getenv('DEBUG') == 'TRUE':
            # Local redis cache
            redis_client = redis.Redis(host='localhost', port=6379)
        else:
            # Elasticache
            username = os.getenv('ELASTICACHE_USERNAME')
            cache_name = os.getenv('CACHE_NAME')
            elasticache_endpoint = os.getenv('ELASTICACHE_ENDPOINT')
            creds_provider = ElastiCacheIAMProvider(user=username, cache_name=cache_name,
                                                is_serverless=True)

            redis_client = redis.Redis(host=elasticache_endpoint, port=6379,
                                        credential_provider=creds_provider, ssl=True,
                                        ssl_cert_reqs="none")
        return redis_client

    def query_comments(self, team_name:str, start_time:int, end_time:int) -> pd.DataFrame:
        """
        Queries for comments by team name and timeframe.

        Args:
            team_name: The name of the team to query.
            start_time: The start of the time window to get comments from.
            end_time: The end of the time window to get comments from.
        
        Returns:
            pd.DataFrame: Dataframe containing the result of the query.
        """
        try:
            comments = self.redis_client.zrangebyscore(f'team:{team_name}', start_time, end_time)
        except redis.exceptions.AuthenticationError:
            # Reinitialize connection to cache if credentials have expired.
            self.redis_client = self.create_redis_client()
            comments = self.redis_client.zrangebyscore(f'team:{team_name}', start_time, end_time)
        return pd.DataFrame([json.loads(comment) for comment in comments])


if __name__ == '__main__':
    # Test comment querying locally:
    c = Comment()
