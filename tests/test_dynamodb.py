import pytest
from moto import mock_aws
import boto3
from decimal import Decimal
from src.processing.comment_table import Comment

@mock_aws
def test_add_comment():
    """
    Tests adding records to dynamoDB and retrieving them.
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table_name = 'reddit_comment_data'
    
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'match_ID_timestamp', 'KeyType': 'HASH'},
            {'AttributeName': 'id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'match_ID_timestamp', 'AttributeType': 'S'},
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    # Instantiate your Comment class and add a record
    comment_table = Comment(dyn_resource=dynamodb)
    comment_table.exists(table_name)
    
    data = {
        'match_keywords': 'goal',
        'timestamp': 1627846262,
        'label': 'positive',
        'score': Decimal('0.9'),
        'id': '12345',
        'name': 'Test Comment',
        'author': 'test_author',
        'body': 'This is a test comment',
        'upvotes': 10,
        'downvotes': 0,
    }
    
    comment_table.add_comment(data=data)
    
    # Verify that the item was added
    response = comment_table.table.get_item(
        Key={'match_ID_timestamp': 'goal_1627846262', 'id': '12345'}
    )
    print(response)
    assert 'Item' in response
    assert response['Item']['sentiment_id'] == 'positive'
    assert response['Item']['sentiment_score'] == Decimal('0.9')
