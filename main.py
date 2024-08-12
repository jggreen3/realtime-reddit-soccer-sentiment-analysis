import boto3
from src.ingestion.reddit_producer import RedditProducer
from src.ingestion.kinesis_stream import KinesisStream
from src.processing.comment_table import Comment

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
# comment_table.exists('reddit_comment_data')

# comment_table.add_comment({'id': 'lhsyiws', 'name': 't1_lhsyiws', 'author': 'goodyear_1678', 'body': 'Hmmm, turns out your lot are a bit too small as well apparently!', 'upvotes': 1, 'downvotes': 0, 'timestamp': 1723495017.0, 'match_keywords': '1', 'sentiment_id': 'Positive'})