"""
Defines a DynamoDB table containing Reddit comment data and methods to interact with that table.
"""

from botocore.exceptions import ClientError

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
                    # 'sentiment_id': data['sentiment_id'],
                    'sentiment_id': 'positive', # For dev, making records show positive
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