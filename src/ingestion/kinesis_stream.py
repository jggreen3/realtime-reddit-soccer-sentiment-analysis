"""This module defines a Kinesis stream, providing methods to get/put records in the
stream"""

import json


class KinesisStream:
    """
    Describes a Kinesis stream
    """

    def __init__(self, kinesis_client) -> None:
        self.name = 'reddit-sentiment-stream'
        self.kinesis_client = kinesis_client

    def put_record(self, data, partition_key):
        """
        Puts data into the stream. The data is formatted as JSON before it is passed
        to the stream.

        Args:
            data: The data to put in the stream.
            partition_key: The partition key to use for the data.
        
        Returns:
            Metadata about the record, including its shard ID and sequence number.
        """
        try:
            json_data = json.dumps(data).encode('utf-8')

            response = self.kinesis_client.put_record(
                StreamName=self.name, Data=json_data, PartitionKey=partition_key
            )
            shard_id = response['ShardId']
            sequence_number = response['SequenceNumber']
            print(f"Put record in stream {self.name} on shard {shard_id} \
                  with sequence number {sequence_number}.")
        except:
            print(f"Couldn't put record in stream {self.name}")
            raise

        return response


    def get_records(self, shard_id, iterator_type='TRIM_HORIZON', limit=10):
        """
        Gets records from the specified shard in the stream.

        Args:
            shard_id: The ID of the shard to get records from.
            iterator_type: The type of shard iterator (e.g., 'TRIM_HORIZON', 'LATEST').
            limit: The maximum number of records to retrieve.
        
        Returns:
            The retrieved records.
        """
        try:
            shard_iterator = self.kinesis_client.get_shard_iterator(
                StreamName=self.name,
                ShardId=shard_id,
                ShardIteratorType=iterator_type
            )['ShardIterator']

            response = self.kinesis_client.get_records(
                ShardIterator=shard_iterator,
                Limit=limit
            )

            records = response['Records']
            for record in records:
                print(f"Record: {json.loads(record['Data'])}")

            return records

        except Exception as e:
            print(f"Couldn't get records from shard {shard_id}. Error: {e}")
            raise
