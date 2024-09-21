"""Defines a lambda function and helper methods."""

import logging
import json
import os
from typing import Any, Optional
import base64
import boto3
from comment_table import Comment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def initialize_resources(sagemaker_runtime=None, comment_table=None, endpoint_name=None) -> tuple:
    """Initializes the required AWS resources if not provided."""
    if sagemaker_runtime is None:
        sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=os.getenv('AWS_REGION'))
    if comment_table is None:
        dyn_resource = boto3.resource('dynamodb')
        comment_table = Comment(dyn_resource=dyn_resource)
        if not comment_table.exists(os.getenv('DYNAMODB_TABLE_NAME')):
            raise RuntimeError(f"DynamoDB table {os.getenv('DYNAMODB_TABLE_NAME')} does not exist.")
    if endpoint_name is None:
        endpoint_name = os.getenv('SAGEMAKER_ENDPOINT_NAME')

    return sagemaker_runtime, comment_table, endpoint_name


def process_record(record: dict[str, Any], sagemaker_runtime, comment_table,
                    endpoint_name: str) -> None:
    """Processes a single Kinesis record."""
    try:
        logger.info("Processing Kinesis Event - EventID: %s", record['eventID'])

        # Decode the base64 encoded data from Kinesis
        decoded_data = base64.b64decode(record['kinesis']['data'])

        # Load the decoded JSON data
        record_data = json.loads(decoded_data)

        # Analyze and store body sentiment
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps({'text': record_data['body']})
        )

        decoded_response = json.loads(response['Body'].read().decode('utf-8'))

        record_data['label'] = decoded_response['label']
        record_data['score'] = decoded_response['score']

        comment_table.add_comment(data=record_data)

    except Exception as e:
        logger.error("An error occurred while processing the record: %s", e)
        raise

def lambda_handler(event: dict[str, Any], context: dict[str, Any], sagemaker_runtime=None,
                    comment_table=None, endpoint_name: Optional[str] = None) -> None:
    """
    Lambda function that calls a SageMaker endpoint and adds records to DynamoDB
    when new records are added to a Kinesis stream.
    """
    # Initialize AWS services
    sagemaker_runtime, comment_table, endpoint_name = initialize_resources(
        sagemaker_runtime, comment_table, endpoint_name
    )

    # Process each record in the event
    for record in event['Records']:
        process_record(record, sagemaker_runtime, comment_table, endpoint_name)
    logger.info("Successfully processed %s records.", len(event['Records']))
