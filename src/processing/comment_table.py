"""
Defines a DynamoDB table containing Reddit comment data and methods to interact with that table.
"""
import logging
from decimal import Decimal
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class Comment:
    """
    Encapsulates a DynamoDB table of comment data.
    """

    def __init__(self,
                 dyn_resource):
        """
        Args:
            dyn_resource: A Boto3 DynamoDB resource.
        """

        self.dyn_resource = dyn_resource
        self.table = None # Table variable is set during call to exists.


    def exists(self, table_name: str) -> bool:
        """
        Determines whether or not a table exsits. If the table exists, stores it as instance
        variable defining table to be used.

        Args:
            table_name: The name of the table to check.

        Returns:
            True when the table exists, False otherwise.
        """

        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            self.table = table
            return True
        except ClientError as err:
            error_code = err.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            logger.error("Couldn't check for existence of table: %s, %s", error_code,
                            err.response['Error']['Message'])
            raise

    def add_comment(self, data: dict) -> None:
        """
        Adds a comment record to the table.
        
        Args:
            data: JSON data containing comment information.
        """
        try:
            self.table.put_item(
                Item=self._prepare_item(data)
            )
        except ClientError as err:
            logger.error("Couldn't add comment to table: %s, %s", err.response['Error']['Code'],
                         err.response['Error']['Message'])
            raise

    def _prepare_item(self, data: dict) -> dict:
        """
        Prepares a DynamoDB item from the provided data.

        Args:
            data: JSON data containing comment information.

        Returns:
            A dictionary representing the DynamoDB item.
        """
        return {
            'team_name': data['team'],
            'comment_id_timestamp': data['id'] + str(int(data['timestamp'])),
            'sentiment_id': data['label'],
            'sentiment_score': Decimal(data['score']),
            'id': data['id'],
            'name': data['name'],
            'author': data['author'],
            'body': data['body'],
            'upvotes': data['upvotes'],
            'downvotes': data['downvotes'],
            'timestamp': int(data['timestamp']),
            'subreddit': data['subreddit']
        }
