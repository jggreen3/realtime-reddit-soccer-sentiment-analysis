#!/bin/bash

# Deploy a new DynamoDB table

echo "Creating DynamoDB table..."

# Set variables
TABLE_NAME=$1  
PARTITION_KEY="team_name"         # Partition key for the table
SORT_KEY="comment_id_timestamp"   # Sort key for the table
READ_CAPACITY_UNITS=5             # Adjust based on your expected read load
WRITE_CAPACITY_UNITS=5            # Adjust based on your expected write load

# Create the DynamoDB table
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=$PARTITION_KEY,AttributeType=S \
        AttributeName=$SORT_KEY,AttributeType=S \
    --key-schema \
        AttributeName=$PARTITION_KEY,KeyType=HASH \
        AttributeName=$SORT_KEY,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=$READ_CAPACITY_UNITS,WriteCapacityUnits=$WRITE_CAPACITY_UNITS

echo "DynamoDB table '$TABLE_NAME' created successfully."
