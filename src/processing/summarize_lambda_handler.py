"""Defines a Lambda function and helper methods to process records from a DynamoDB stream."""

from typing import Any, Tuple, Union
import os
import logging
import json
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import ParseResult, urlencode, urlunparse
import redis
import botocore.session
from botocore.model import ServiceId
from botocore.signers import RequestSigner
from cachetools import TTLCache, cached
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

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


def create_llm_chain():
    """Creates a langchain Chain operation to interact with an LLM and parse the response"""
    llm = ChatOpenAI(organization=os.getenv('OPENAI_ORGANIZATION'),
                     model='gpt-4o-mini')

    parser = StrOutputParser()

    prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Summarize the most common topics in the following group of comments. \
     Tailor your summary for Premier League fans. Return an ordered list going from most common \
      to least common topic in the form : **Broad topic** - Elaboration on specific details."),
    ("user", "{comment}")])

    return prompt_template | llm | parser


def get_comments_for_summarization(redis_client: redis.Redis, start_time: datetime,
                                    end_time:datetime, team_name:str) -> list[str]:
    """Retrieve comments from Redis for the specified team within the specified time window."""
    try:
        records = redis_client.zrangebyscore(f'team:{team_name}',
                                            int(start_time.timestamp()), int(end_time.timestamp()))
    except Exception as e:
        logger.info('error in get comments function: %s', e)
        
    return [json.loads(record)['body'] for record in records]



def summarize_comments(comments: list[str], chain) -> str:
    """Summarizes comments by invoking LangChain chain."""
    comment_text = ' '.join(comments)
    summary = chain.invoke({"comment": comment_text}).strip()
    return summary



def store_summary(summary:str, start_time:datetime, team_name:str,
                   redis_client:redis.Redis):
    """Store the summary in Redis"""

    redis_client.zadd(f'team_summary:{team_name}', {summary:int(start_time.timestamp())})



def process_team_comments(team_name: str, start_time: datetime, end_time: datetime,
                          redis_client: redis.Redis, chain) -> None:
    """Fetch, summarize, and store comments for a specific team."""
    try:
        # Fetch comments
        logger.info('Getting comments for team: %s', team_name)
        comments = get_comments_for_summarization(redis_client, start_time, end_time, team_name)
        if comments:
            # Summarize comments
            logger.info('Summarizing comments for team: %s', team_name)
            summary = summarize_comments(comments, chain)
            # Store summary in Redis
            store_summary(summary, start_time, team_name, redis_client)
            logger.info('Processed and stored summary for team: %s', team_name)
        else:
            logger.info("No comments found for team %s during this time window.", team_name)
    except Exception as e:
        logger.error("Error processing team %s: %s", team_name, e)



def lambda_handler(event: dict[str, Any], context: dict[str, Any]):
    """Lambda function that processes comments for multiple teams in parallel."""

    username = os.getenv('ELASTICACHE_USERNAME')
    cache_name = os.getenv('CACHE_NAME')
    elasticache_endpoint = os.getenv('ELASTICACHE_ENDPOINT')
    creds_provider = ElastiCacheIAMProvider(user=username, cache_name=cache_name,
                                             is_serverless=True)

    redis_client = redis.Redis(host=elasticache_endpoint, port=6379,
                               credential_provider=creds_provider, ssl=True, ssl_cert_reqs="none")
    
    logger.info("ping result: %s", redis_client.ping())

    # Define the time window
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=20)

    # List of teams
    teams = ['arsenal', 'aston villa', 'bournemouth', 'brentford', 'brighton', 'chelsea',
            'crystal palace', 'everton', 'fulham', 'ipswich town', 'leicester city', 'liverpool',
            'manchester city', 'manchester united', 'newcastle', 'nottingham forest',
            'southampton', 'tottenham', 'west ham', 'wolves']

    # Create the LangChain chain for summarization
    chain = create_llm_chain()

    # Process each team's comments in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(teams)) as executor:
        futures = []
        for team in teams:
            futures.append(executor.submit(process_team_comments, team, start_time,
                                            end_time, redis_client, chain))

        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()  # Raises an exception if the thread encountered one
            except Exception as e:
                logger.error("Error in thread execution: %s", e)

    logger.info("Successfully processed comments for all teams.")
