"""Defines a Lambda function and helper methods to process records from a DynamoDB stream."""

from typing import Any, Tuple, Union
import os
import logging
import json
from urllib.parse import ParseResult, urlencode, urlunparse
import redis
import botocore.session
from botocore.model import ServiceId
from botocore.signers import RequestSigner
from cachetools import TTLCache, cached


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


def _prepare_item(data:dict) -> dict:
    """Prepares a Redis item from the provided data
    
    Args:
        data: JSON data containing DynamoDB insert information.
    
    Returns:
        A dictionary representing the inserted item."""

    return {
        'sentiment_score': data['sentiment_score']['N'],
        'sentiment_id': data['sentiment_id']['S'],
        'upvotes': data['upvotes']['N'],
        'author': data['author']['S'],
        'name': data['name']['S'],
        'id': data['id']['S'],
        'body': data['body']['S'],
        'downvotes': data['downvotes']['N'],
        'subreddit': data['subreddit']['S'],
        'timestamp': data['timestamp']['N']
    }

def process_record(record: dict[str, Any], redis_client: redis.Redis) -> None:
    """Processes a single DynamoDB Stream record."""
    try:
        logger.info("Processing DynamoDB Stream Event: %s", record['eventID'])
        new_data = record['dynamodb']['NewImage']
        prepared_data = _prepare_item(new_data)
        team_name = record['dynamodb']['Keys']['team_name']['S']
        timestamp = record['dynamodb']['NewImage']['timestamp']['N']

        logger.info("Team_name: %s, timestamp: %s, data: %s", team_name, timestamp,
                     json.dumps(prepared_data))
        
        redis_client.zadd(f'team:{team_name}', {json.dumps(prepared_data):timestamp})

        logger.info("Added comment to Redis cache.")

    except Exception as e:
        logger.error("An error occured while processing the record: %s", e)
        raise

def lambda_handler(event: dict[str, Any], context:dict[str, Any]):
    """Lambda function that adds records from a dynamoDB stream to 
    redis cache."""

    username = os.getenv('ELASTICACHE_USERNAME')
    cache_name = os.getenv('CACHE_NAME')
    elasticache_endpoint = os.getenv('ELASTICACHE_ENDPOINT')
    creds_provider = ElastiCacheIAMProvider(user=username, cache_name=cache_name,
                                             is_serverless=False)

    redis_client = redis.Redis(host=elasticache_endpoint, port=6379,
                                credential_provider=creds_provider, ssl=True, ssl_cert_reqs="none")

    logger.info("ping result: %s", redis_client.ping())
    for record in event['Records']:
        process_record(record, redis_client)
