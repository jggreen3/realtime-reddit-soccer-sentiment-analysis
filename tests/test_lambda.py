# import pytest
# from moto import mock_aws
# import boto3
# import json
# from src.processing.lambda_handler import lambda_handler
# from src.processing.comment_table import Comment
# import base64
# from unittest.mock import Mock
# import io
# from decimal import Decimal

# @mock_aws
# def test_lambda_handler():
#     # Mock Kinesis and DynamoDB
#     kinesis_client = boto3.client('kinesis', region_name='us-west-1')
#     kinesis_client.create_stream(StreamName='realtime-soccer-sentiment-analysis', ShardCount=1)
    
#     dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
#     table_name = 'reddit_comment_data'
#     table = dynamodb.create_table(
#         TableName=table_name,
#         KeySchema=[
#             {'AttributeName': 'match_ID_timestamp', 'KeyType': 'HASH'},
#             {'AttributeName': 'id', 'KeyType': 'RANGE'}
#         ],
#         AttributeDefinitions=[
#             {'AttributeName': 'match_ID_timestamp', 'AttributeType': 'S'},
#             {'AttributeName': 'id', 'AttributeType': 'S'}
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 5,
#             'WriteCapacityUnits': 5
#         }
#     )

#     comment_table = Comment(dyn_resource=dynamodb)
#     comment_table.exists(table_name)

#     # Mock SageMaker response
#     mock_sagemaker_client = Mock()
#     mock_sagemaker_client.invoke_endpoint.return_value = {
#         'Body': io.BytesIO(json.dumps({
#             'label': 'positive',
#             'score': 1
#         }).encode('utf-8'))
#     }

#     # Mock Event
#     event = {
#         'Records': [
#             {
#                 'eventID': '1',
#                 'kinesis': {
#                     'data': base64.b64encode(json.dumps({
#                         'match_keywords': 'goal',
#                         'timestamp': '1627846262',
#                         'id': '12345',
#                         'name': 'Test Comment',
#                         'author': 'test_author',
#                         'body': 'This is a test comment',
#                         'upvotes': '10',
#                         'downvotes': '1',
#                     }).encode('utf-8')).decode('utf-8')
#                 }
#             }
#         ]
#     }

#     # Call the Lambda function
#     lambda_handler(event, None, sagemaker_runtime=mock_sagemaker_client, comment_table=comment_table, endpoint_name='mock-endpoint')

#     # Validate that the data was added to DynamoDB
#     response = table.get_item(
#         Key={'match_ID_timestamp': 'goal_1627846262', 'id': '12345'}
#     )
#     assert 'Item' in response
#     assert response['Item']['body'] == 'This is a test comment'
#     assert response['Item']['label'] == 'positive'
#     assert response['Item']['score'] == 0.9
