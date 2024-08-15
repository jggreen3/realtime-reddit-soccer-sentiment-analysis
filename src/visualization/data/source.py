"""
Defines a DynamoDB table containing Reddit comment data and methods to interact with that table.
"""
from decimal import Decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import pandas as pd

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
        # Table variable is set during call to exists.
        self.table = None


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
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                print(f"Couldnt check for existence: {err.response['Error']['Code']}, \
                      {err.response['Error']['Message']}")


        self.table = table

        return exists



    def add_comment(self, data: dict):
        """
        Adds a comment record to the table.
        
        Args:
            data: Json data containing comment information
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
            print(f"Couldnt add comment to table: {err.response['Error']['Code']}, \
                      {err.response['Error']['Message']}")
            

    def query_comments(self, team_name) -> pd.DataFrame:
        """
        Queries for comments with a specific match id and date key.

        Args:
        team_name: The team name to query
        
        Returns:
        Pandas dataframe containing comments which match the specified match id and date.
        """

        try:
            response = self.table.query(KeyConditionExpression=Key("team_name")
                                        .eq(team_name))
        except ClientError as err:
            print(f"Couldnt query for comments with {team_name}: \
                  {err.response['Error']['Code']}, {err.response['Error']['Message']}")
        else:
            return pd.DataFrame(response["Items"])
