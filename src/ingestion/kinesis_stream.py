"""This module defines a Kinesis stream, providing methods to get/put records in the
stream"""

import json
import logging
import dotenv
import os

logger = logging.getLogger(__name__)
dotenv.load_dotenv()

class KinesisStream:
    """
    Describes a Kinesis stream
    """

    def __init__(self, kinesis_client) -> None:
        self.name = os.getenv('KINESIS_STREAM_NAME')
        self.kinesis_client = kinesis_client

    def put_record(self, data: dict, partition_key: str) -> dict:
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
        except Exception as e:
            logger.error("Couldn't put record in stream %s. Error: %s", self.name, e)
            raise

        return response


    def get_records(self, shard_id: str, iterator_type: str = 'TRIM_HORIZON',
                     limit: int =10) -> list[dict]:
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
            return [json.loads(record['Data']) for record in records]

        except Exception as e:
            logger.error("Couldn't get records from shard %s. Error: %s", shard_id, e)
            raise
