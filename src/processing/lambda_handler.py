import json
import boto3
import base64
from src.processing.comment_table import Comment


def lambda_handler(event, context, sagemaker_runtime=None, comment_table=None, endpoint_name=None):
    """
    Defines a lambda function which calls a sagemaker endpoint and adds records to dynamodb
    when new records are added to a Kinessi stream.
    """
    # Set variables for aws services
    if sagemaker_runtime is None:
        sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='us-west-1')
    if comment_table is None:
        dyn_resource = boto3.resource('dynamodb')
        comment_table = Comment(dyn_resource=dyn_resource)
        comment_table.exists('soccer_comment_data')
    if endpoint_name is None:
        endpoint_name = 'huggingface-pytorch-inference-2024-08-13-17-04-51-738'


    for record in event['Records']:
        try:
            print(f"Processed Kinesis Event - EventID: {record['eventID']}")

            # Decode the base64 encoded data from Kinesis
            decoded_data = base64.b64decode(record['kinesis']['data'])

            # Load the decoded json data
            record_data = json.loads(decoded_data)

            # Analyze and store body sentiment
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name, 
                ContentType='application/json',  # Set the content type,
                Body=json.dumps({'text': record_data['body']}))


            decoded_response = json.loads(response['Body'].read().decode('utf-8'))

            record_data['label'] = decoded_response['label']
            record_data['score'] = decoded_response['score']

            comment_table.add_comment(data=record_data)
        except Exception as e:
            print(f"An error occurred {e}")
            raise e
    print(f"Successfully processed {len(event['Records'])} records.")
