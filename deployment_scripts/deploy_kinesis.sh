#!/bin/bash
# Deploy Kinesis stream

echo "Creating Kinesis stream..."

# Set variables
STREAM_NAME=$1

# Create Kinesis stream
aws kinesis create-stream --stream-name $STREAM_NAME --shard-count 1

echo "Kinesis stream created successfully."
