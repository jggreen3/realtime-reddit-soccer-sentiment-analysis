"""
This module defines and initiates a reddit comment stream from PRAW. Based on the subbreddit and post keyword arguments,
it matches and streams comments related to a specific topic.
"""

import os
import praw
import dotenv


from src.processing.sentiment_analysis import predict

dotenv.load_dotenv()


class RedditContentStream:
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
                        post_keywords: list=None):
        """
        Build a comment stream from PRAW.

        Args:
            post_keywords (lst[str]): List of keywords to match to the parent post for each comment. OPTIONAL FOR DEV ONLY!!!

        Notes:
            Currently, for a comment to count as matching, it only has to contain one keyword from the list.
            Additionally, only the post title is checked (not selftext) because r/soccer doesn't allow selfposts.
        """

        for comment in self.reddit.subreddit(self.subreddit).stream.comments():
            if post_keywords:
                if any(keyword in comment.submission.title.lower() for keyword in post_keywords):
                    l, s = predict(comment.body)
                    print(f'{comment.body}, {l}: {s}')    
                
            else:
                l, s = predict(comment.body)
                print(f'{comment.body}, {l}: {s}')


if __name__ == '__main__':
    stream = RedditContentStream()
    stream.stream_comments(post_keywords=['Argentina', 'france'])

