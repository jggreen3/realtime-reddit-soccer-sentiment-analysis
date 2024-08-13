from __future__ import absolute_import
import pytest
from moto import mock_aws
import boto3
from src.ingestion.kinesis_stream import KinesisStream

@mock_aws
def test_put_record():
    """"
    Test KinesisStream class and putting records in stream. 
    """
    kinesis_client = boto3.client('kinesis', region_name='us-west-1')
    kinesis_client.create_stream(StreamName='reddit-sentiment-stream', ShardCount=1)
    stream = KinesisStream(kinesis_client=kinesis_client)
    
    data = {'id': '123', 'body': 'Test comment'}
    partition_key = 'test_key'
    
    response = stream.put_record(data=data, partition_key=partition_key)
    
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert 'ShardId' in response
    assert 'SequenceNumber' in response
