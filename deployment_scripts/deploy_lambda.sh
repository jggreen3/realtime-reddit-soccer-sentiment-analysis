#!/bin/bash

echo "Deploying Lambda function"

# Set variables
LAMBDA_FUNCTION_NAME=$1
ROLE=$2
ZIP_FILE="lambda_function.zip"

# Package the lambda function comment table into a zip file
cd ../src/processing/package
zip -r ../$ZIP_FILE .
cd ..
zip -r $ZIP_FILE lambda_handler.py
zip -r $ZIP_FILE comment_table.py

aws lambda create-function --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://$ZIP_FILE \
    --handler lambda_handler.lambda_handler --runtime python3.8 --role $2

echo "Lambda function deployed successfully."