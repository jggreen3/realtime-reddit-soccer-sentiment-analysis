import boto3
from src.ingestion.reddit_producer import RedditProducer
from src.ingestion.kinesis_stream import KinesisStream
from src.processing.comment_table import Comment
import json

# Build kinesis client
kinesis_client = boto3.client('kinesis', region_name='us-west-1')

# Instantiate kinesis stream with client
kinesis_stream = KinesisStream(kinesis_client=kinesis_client)

# Instantiate reddit producer
stream = RedditProducer()

# Start streaming reddit comments, passing kinesis stream
stream.stream_comments(kinesis_stream=kinesis_stream, post_keywords='')

# dyn_resource = boto3.resource('dynamodb')

# comment_table = Comment(dyn_resource=dyn_resource)
# comment_table.exists('comment_data')

# comment_table.add_comment({'id': 'lhsyiws', 'name': 't1_lhsyiws', 'author': 'goodyear_1678', 'body': 'Hmmm, turns out your lot are a bit too small as well apparently!', 'upvotes': 1, 'downvotes': 0, 'timestamp': 1723495017.0, 'match_keywords': '1', 'label': 'Positive', 'score': 1})

# sagemaker_runtime = boto3.client(
#     "sagemaker-runtime", region_name='us-west-1')

# # The endpoint name must be unique within 
# # an AWS Region in your AWS account. 
# endpoint_name='huggingface-pytorch-inference-2024-08-13-17-04-51-738'

# response = sagemaker_runtime.invoke_endpoint(
#     EndpointName=endpoint_name, 
#     ContentType='application/json',  # Set the content type,
#     Body=(json.dumps({'text': 'This game is amazing!!'}))
#     )

# # Decodes and prints the response body:
# decoded_response = json.loads(response['Body'].read().decode('utf-8'))
# print(decoded_response)

# print(decoded_response['label'])
