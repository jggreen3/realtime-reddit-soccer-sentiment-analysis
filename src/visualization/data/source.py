"""
Defines a DynamoDB table containing Reddit comment data and methods to interact with that table.
"""
import logging
from decimal import Decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import pandas as pd

logger = logging.getLogger(__name__)

class Comment:
    """
    Encapsulates a DynamoDB table of comment data.
    """

    def __init__(self, dyn_resource):
        """
        Args:
            dyn_resource: A Boto3 DynamoDB resource.
        """

        self.dyn_resource = dyn_resource
        self.table = None  # Table variable is set during call to exists.

    def exists(self, table_name: str) -> bool:
        """
        Determines whether or not a table exists. If the table exists, stores it as an instance
        variable defining the table to be used.

        Args:
            table_name: The name of the table to check.

        Returns:
            True when the table exists, False otherwise.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error("Couldn't check for existence: %s, %s",
                             err.response['Error']['Code'], err.response['Error']['Message'])
                raise

        self.table = table
        return exists

    def add_comment(self, data: dict) -> None:
        """
        Adds a comment record to the table.
        
        Args:
            data: JSON data containing comment information.
        """
        try:
            self.table.put_item(
                Item={
                    'match_ID_timestamp': data['match_keywords'] + '_' + str(data['timestamp']),
                    'sentiment_id': data['label'],
                    'sentiment_score': Decimal(data['score']),
                    'id': data['id'],
                    'name': data['name'],
                    'author': data['author'],
                    'body': data['body'],
                    'upvotes': data['upvotes'],
                    'downvotes': data['downvotes'],
                    'timestamp': int(data['timestamp']),
                }
            )
        except ClientError as err:
            logger.error("Couldn't add comment to table: %s, %s",
                         err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def query_comments(self, team_name: str) -> pd.DataFrame:
        """
        Queries for comments with a specific team name.

        Args:
            team_name: The team name to query.
        
        Returns:
            pd.DataFrame: DataFrame containing comments that match the specified team name.
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key("team_name").eq(team_name)
            )
        except ClientError as err:
            logger.error("Couldn't query for comments with %s: %s, %s",
                         team_name, err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        
        return pd.DataFrame(response["Items"])
