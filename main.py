import boto3
from src.ingestion.reddit_producer import RedditProducer
from src.ingestion.kinesis_stream import KinesisStream

# Build kinesis client
kinesis_client = boto3.client('kinesis', region_name='us-west-1')

# Instantiate kinesis stream with client
kinesis_stream = KinesisStream(kinesis_client=kinesis_client)

#Instantiate reddit producer
stream = RedditProducer()

# Start streaming reddit comments, passing kinesis stream
stream.stream_comments(kinesis_stream=kinesis_stream, post_keywords='')
