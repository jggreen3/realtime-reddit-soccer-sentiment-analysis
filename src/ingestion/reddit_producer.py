"""
This module defines and initiates a reddit comment stream from PRAW. Based on the subbreddit 
and post keyword arguments, it matches and streams comments related to a specific topic.
"""

import os
import logging
from typing import Optional
import praw
import dotenv
from src.ingestion.kinesis_stream import KinesisStream
# from kinesis_stream import KinesisStream

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class RedditProducer:
    """
    Wrapper for the PRAW API, initiating and managing a comment stream.
    Inputs:

    Args: 
        include_individual_subreddits (bool): 
            - True: All individual team subreddits + r/soccer
            - False: r/soccer comments only
    """

    SUBREDDIT_MAP = {
        'Gunners': 'arsenal', 'avfc': 'aston villa',
        'AFCBournemouth': 'bournemouth', 'Brentford': 'brentford',
        'BrightonHoveAlbion': 'brighton', 'chelseafc': 'chelsea',
        'crystalpalace': 'crystal palace', 'Everton': 'everton',
        'FulhamFC': 'fulham', 'IpswichTownFC': 'ipswich town',
        'lcfc': 'leicester city', 'LiverpoolFC': 'liverpool',
        'MCFC': 'manchester city', 'reddevils': 'manchester united',
        'nufc': 'newcastle', 'nffc': 'nottingham forest',
        'SaintsFC': 'southampton', 'coys': 'tottenham',
        'Hammers': 'west ham', 'WWFC': 'wolves'
    }

    def __init__(self,
                 include_individual_subreddits: bool = False):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT')
        self.reddit = self.build_service()
        self.subreddit = self.build_subreddit_list(include_individual_subreddits)


    def build_service(self):
        """"
        Builds and returns a PRAW reddit object.
        """
        return praw.Reddit(client_id=self.client_id,
                           client_secret=self.client_secret,
                           user_agent=self.user_agent)


    def build_subreddit_list(self, include_individual_subreddits: bool) -> str:
        """
        Builds and returns a list of subreddits to monitor.
        """
        if include_individual_subreddits:
            return '+'.join(list(self.SUBREDDIT_MAP.keys()) + ['Soccer'])
        return 'Soccer'


    def stream_comments(self, kinesis_stream: Optional[KinesisStream] = None) -> None:
        """
        Streams comments from Reddit and sends them to a Kinesis stream if provided.

        Args:
            kinesis_stream (Optional[KinesisStream]): Stream definition to add comment records.

        Notes:
            A comment matches if it contains at least one team name in the submission title.
            Only r/soccer post titles are checked, as r/soccer doesn't allow selfposts.
        """
        for comment in self.reddit.subreddit(self.subreddit).stream.comments(skip_existing=True):
            try:
                teams = self.extract_teams(comment)
                if not teams:
                    continue

                for team in teams:
                    comment_json = self.build_comment_json(comment, team)
                    logger.info('Processing comment: %s', comment_json)

                    if kinesis_stream:
                        kinesis_stream.put_record(data=comment_json, partition_key=team)

            except Exception as e:
                logger.error('An error occurred: %s', e)


    def extract_teams(self, comment) -> list[str]:
        """Extracts and returns a list of teams mentioned in a comment's parent post title."""
        if comment.subreddit.display_name == 'soccer':
            return [name for name in self.SUBREDDIT_MAP.values()
                    if name in comment.submission.title.lower()]
        return [self.SUBREDDIT_MAP.get(comment.subreddit.display_name, '')]


    def build_comment_json(self, comment, team: str) -> dict:
        """Builds and returns a JSON-serializable dictionary of comment details."""
        return {
            'id': comment.id,
            'name': comment.name,
            'author': comment.author.name if comment.author else 'N/A',
            'body': comment.body,
            'upvotes': comment.ups,
            'downvotes': comment.downs,
            'timestamp': comment.created_utc,
            'subreddit': comment.subreddit.display_name,
            'team': team
        }


if __name__ == '__main__':
    stream = RedditProducer(include_individual_subreddits=True)
    stream.stream_comments()
