"""
This module defines and initiates a reddit comment stream from PRAW. Based on the subbreddit 
and post keyword arguments, it matches and streams comments related to a specific topic.
"""

import os
import praw
import dotenv
from src.ingestion.kinesis_stream import KinesisStream


dotenv.load_dotenv()


class RedditProducer:
    """
    Class which acts as a wrapper for the PRAW API, initiating and managing a comment stream.
    Inputs:

    Args: 
        Subreddit (str): Subreddit from which to stream comments
    """
    def __init__(self,
                 subreddit='Soccer'):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT')
        self.subreddit = subreddit
        # self.model = SentimentAnalysisModel()

        self.reddit = self.build_service()

    def build_service(self):
        """"
        Builds a PRAW reddit service.

        Returns:
            Praw.Reddit object
        """

        return praw.Reddit(client_id=self.client_id,
                           client_secret=self.client_secret,
                           user_agent=self.user_agent)

    def stream_comments(self,
                        post_keywords: list=None,
                        kinesis_stream: KinesisStream=None):
        """
        Build a comment stream from PRAW.

        Args:
            post_keywords (lst[str]): List of keywords to match to the parent post for each comment.
              OPTIONAL FOR DEV ONLY!!!
            kinesis_stream KinesisStream: Stream definition which defines where to add comment 
            records
            

        Notes:
            Currently, for a comment to count as matching, it only has to contain one keyword 
            from the list. Additionally, only the post title is checked (not selftext) because 
            r/soccer doesn't allow selfposts.
        """

        for comment in self.reddit.subreddit(self.subreddit).stream.comments(skip_existing=True):
            try:
                if post_keywords:
                    if not any(keyword in comment.submission.title.lower()
                                for keyword in post_keywords):
                        continue

                if post_keywords:
                    parition_key = '-'.join(post_keywords)
                else:
                    parition_key = '1'

                comment_json = {
                    'id': comment.id,
                    'name': comment.name,
                    'author': comment.author.name,
                    'body': comment.body,
                    'upvotes': comment.ups,
                    'downvotes': comment.downs,
                    'timestamp': comment.created_utc,
                    'match_keywords': parition_key
                }
                print(comment_json)

                kinesis_stream.put_record(data=comment_json, partition_key=parition_key)
                
                
            except Exception as e:
                print(f'An error occured: {str(e)}')

if __name__ == '__main__':
    stream = RedditProducer()
    stream.stream_comments(post_keywords=None)
