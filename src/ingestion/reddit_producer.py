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
        include_individual_subreddits (bool): Boolean flag to decide whether to include all 
        individual team subreddit submissions or just submissions from r/soccer:
            True: All individual team subreddits + r/soccer
            False: r/soccer comments onle
    """
    def __init__(self,
                 include_individual_subreddits: False):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT')
        self.reddit = self.build_service()
        self.subreddit_map = {'Gunners': 'arsenal', 'avfc': 'aston villa',
                               'AFCBournemouth': 'bournemouth', 'Brentford': 'brentford',
                               'BrightonHoveAlbion': 'brighton', 'chelseafc': 'chelsea',
                               'crystalpalace': 'crystal palace', 'Everton': 'everton',
                               'FulhamFC': 'fulham', 'IpswichTownFC': 'ipswich town',
                               'lcfc': 'leicester city', 'LiverpoolFC': 'liverpool',
                               'MCFC': 'manchester city', 'reddevils': 'manchester united',
                               'nufc': 'newcastle', 'nffc': 'nottingham forest',
                               'SaintsFC': 'southampton', 'coys': 'tottenham',
                               'Hammers': 'west ham', 'WWFC': 'wolves'}

        if include_individual_subreddits:
            self.subreddit = '+'.join(list(self.subreddit_map.keys()) + ['Soccer'])
        else:
            self.subreddit = 'Soccer'



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
                if comment.subreddit.display_name == 'soccer': 
                    teams = [name for name in self.subreddit_map.values() if 
                             name in comment.submission.title.lower()]
                    if len(teams) == 0:
                        continue
                else:
                    teams = [self.subreddit_map[comment.subreddit.display_name]]

                subreddit = comment.subreddit.display_name

                # Loop through teams in case multiple team names match a comment from r/soccer
                for team in teams:
                    comment_json = {
                        'id': comment.id,
                        'name': comment.name,
                        'author': comment.author.name,
                        'body': comment.body,
                        'upvotes': comment.ups,
                        'downvotes': comment.downs,
                        'timestamp': comment.created_utc,
                        'subreddit': subreddit,
                        'team': team
                    }
                    print(comment_json)

                    kinesis_stream.put_record(data=comment_json, partition_key=team)


            except Exception as e:
                print(f'An error occured: {e}')

if __name__ == '__main__':
    stream = RedditProducer(include_individual_subreddits=True)
    stream.stream_comments()
