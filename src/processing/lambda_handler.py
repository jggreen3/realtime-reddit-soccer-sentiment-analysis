import json
import boto3
import base64
from comment_table import Comment
from sentiment_analysis import SentimentAnalysisModel


def lambda_handler(event, context):

    dyn_resource = boto3.resource('dynamodb')
    comment_table = Comment(dyn_resource=dyn_resource)
    comment_table.exists('reddit_comment_data')

    
    model = SentimentAnalysisModel()

    for record in event['Records']:
        try:
            print(f"Processed Kinesis Event - EventID: {record['eventID']}")

            # Decode the base64 encoded data from Kinesis
            decoded_data = base64.b64decode(record['kinesis']['data'])

            # Load the decoded json data
            record_data = json.loads(decoded_data)

            # Analyze and store body sentiment
            label, score = model.predict(decoded_data['body'])
            decoded_data['label'] = label
            decoded_data['score'] = score

            comment_table.add_comment(data=record_data)
        except Exception as e:
            print(f"An error occurred {e}")
            raise e
    print(f"Successfully processed {len(event['Records'])} records.")
