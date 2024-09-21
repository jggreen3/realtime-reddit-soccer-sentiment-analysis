#!/bin/bash

echo "Deploying Lambda function"

# Set variables
LAMBDA_FUNCTION_NAME=$1
ROLE=$2
ZIP_FILE="lambda_function.zip"

# Step 1: Install boto3 into a directory called 'package'
mkdir -p ../src/processing/package
pip install --target ../src/processing/package boto3

# Step 2: Package the 'package' directory into a zip file
cd ../src/processing/package
zip -r9 ../$ZIP_FILE .

# Step 3: Add the lambda function files to the zip file
cd ..
zip -g $ZIP_FILE lambda_handler.py
zip -g $ZIP_FILE comment_table.py

# Step 4: Deploy the Lambda function
aws lambda create-function --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://$ZIP_FILE \
    --handler lambda_handler.lambda_handler --runtime python3.12 --role $ROLE

echo "Lambda function deployed successfully."
