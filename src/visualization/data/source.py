"""Defines a redis cache containing Reddit comment data and methods to interact with it."""

import logging
from urllib.parse import ParseResult, urlencode, urlunparse
from typing import Tuple, Union
import json
import os
import re
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
    

    def get_most_recent_summary(self, team_name:str) -> pd.DataFrame:
        """
        Returns the most recent summary the specified team.

        Args:
            team_name: The name of the team to query.
            start_time: The start of the time window to get comments from.
            end_time: The end of the time window to get comments from.
        
        Returns:
            pd.DataFrame: Dataframe containing the result of the query.
        """
        try:
            summaries = self.redis_client.zrevrangebyscore(f'team_summary:{team_name}', 9027050936,
                                                           1007052007, withscores=True,
                                                            start=0, num=3)
        except redis.exceptions.AuthenticationError:
            # Reinitialize connection to cache if credentials have expired.
            self.redis_client = self.create_redis_client()
            summaries = self.redis_client.zrevrangebyscore(f'team_summary:{team_name}', 9027050936,
                                                           1007052007, withscores=True,
                                                            start=0, num=3)
        df = pd.DataFrame()
        for summary in summaries:
            summary_text = summary[0].decode('utf-8')

            # Find all matches (rank, title, description)
            pattern = r"(\d+)\. \*\*(.*?)\*\* - (.*?)(?=\n\d+\. |\Z)"
            matches = re.findall(pattern, summary_text, re.DOTALL)

            # Convert the matches into a dataframe
            _df = pd.DataFrame(matches, columns=['Rank', 'Title', 'Description'])
            _df['timestamp'] = summary[1]
            
            df = pd.concat([df, _df], axis=0)

        return df.reset_index().sort_values(by='timestamp', ascending=False).iloc[0:6]


if __name__ == '__main__':
    # Test comment querying locally:
    c = Comment()
    print(c.get_most_recent_summary(team_name='arsenal'))
