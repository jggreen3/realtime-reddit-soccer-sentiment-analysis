# Real-Time Premier League Sentiment Dashboard

Welcome to the real-time premier league sentiment dashboard! This project is an application designed
to monitor and visualize fan sentiment across Premier League teams in real-time using Reddit
comments. The dashboard is powered by a scalable AWS backend and a dynamic front-end built with Dash. 

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#architecture">Architecture</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About the Project
Football (or soccer) has an immense global community where fans express their passion, joy,
frustration, and opinions through various platforms, with Reddit being one of the most prominent.
This project was inspired by the desire to track how fans feel about their favorite teams as the 
season progresses. By analyzing the sentiment in Reddit comments, this project provides insights
into how public opinion shifts over time, influenced by match results, player performance, and team
standings.

A sample of what the dashboard looks like running is shown below:

<br>
<div align="center">
    <img src="screenshots/dashboard.png" alt="dashboard" >
</div>

### Architecture:

#### Data Ingestion:
<ul>
    <li><strong>Reddit Comment Collection:</strong> Using the PRAW API, the application continuously 
    streams comments from r/soccer and the largest subreddit for each individual Premier League 
    team.</li>
    <li><strong>Data Streaming:</strong> AWS Kinesis is used to stream data in real-time. As comments
    are generated by PRAW, they are serialized and placed in a Kinesis stream.</li>
    <li><strong>Data Processing:</strong> AWS Lambda functions are employed to process records as
    they come in through the Kinesis stream. The Lamda function invokes a SageMaker enpoint for
    real-time inference, and stores the results in DynamoDB.</li>
</ul>

#### Sentiment Analysis
<ul>
    <li><strong>Model:</strong> Comment sentiment is determined through a pre-trained Hugging
    Face 'RoBERTa' model fine-tuned on Twitter data. This model is well-suited for short text and
    social media content, making it ideal for this use case.</li>
    <li><strong>Real-time Inference:</strong> A SageMaker endpoint is used to perform real-time
    sentiment analysis of incoming comments. Each comment is classified as positive, negative, or
    neutral, and this label, along with the sentiment score, is stored in DynamoDB.</li>
</ul>

#### Visualization
<ul>
    <li><strong>Dashboard:</strong>The front-end is built using Dash, leveraging Plotly for dynamic
    visualizations and Dash Boostrap Components for layout and control components. The dashboard
    provides a real-time view of sentiment trents, comment volume, and sentiment distribution for
    different teams.</li>
</ul>

<br>

The diagram below shows a high-level overview of the cloud architecture for this project.

<br>
<div align="center">
    <img src="screenshots/architecture_diagram.png" alt="architecture diagram" >
</div>


## Getting Started:

### Prerequisistes:

Before you begin, ensure you have the following requirements:

<ul>
    <li><strong>Python 3.8+ </strong></li>
    <li><strong>An AWS Account</strong></li>
    <li><strong>The AWS CLI Installed</strong></li>
    <li><strong>A Reddit developer account and PRAW credentials</strong></li>
</ul>

### Installation:

1. Clone the repository:
    ```shell
    git clone https://github.com/jggreen3/realtime-reddit-soccer-sentiment-analysis.git
    cd realtime-reddit-soccer-sentiment-analysis
    ```

2. Install dependencies (Reccomended to do this in a virtual environment of your choice):
    ```shell
    pip install -r requirements.txt
    ```

3. Configure AWS Credentials:

    Ensure that your AWS credentials are configured locally. You can set up credentials with the aws
    cli.
   
    ```
    aws configure
    ```

5. Create an IAM role for lambda:
    <br>

    In the AWS IAM console, create a role with the following policies attached:
    <ul>
        <li> AmazonDynamoDBFullAccess
        <li> AmazonSageMakerFullAccess
        <li> AWSLambdaKinesisExecutionRole
    </ul>

    These permissions will allow the lambda function to interact with all of the required infastructure.

6. Deploy AWS Resources:

    You can automate the deployment of the Lambda Function, SageMaker Endpoint, and Kinesis Stream
    using the provided shell/python deployment scripts. 

    First, change to the deployment_scripts directory

    ```
    cd deployment_scripts
    ```
<ul>
    <li><strong> Deploy Lambda Function:</strong></li>

```shell
./deploy_lambda.sh my_lambda_function arn:aws:iam::123456789/my-role-name 
```
Here the first argument passed to the script is the desired lambda function name and the second
is the arn number for the Lambda IAM role created in step 4.

<li><strong>Deploy Sagemaker Endpoint:</strong></li>

```
python3 deploy_model.py
```
This script will take about 5 minutes to run

<li><strong>Deploy Kinesis Stream:</strong></li>

```shell
./deploy_kinesis.sh my_stream_name
```
Here the argument passed is the desired name for the kinesis stream being created

<li><strong>Deploy DynamoDB Table:</strong></li>

```shell
./deploy_dynamodb.sh my_table_name
```
Here, the argument passed is the desired name for the dynamodb table being created.

</ul>

6. Set environmental Variables:
Create a `.env` file and add the necessary configuration values. The reddit client and secret ids
as well as the user agent come from PRAW configurations, the sagemaker endpoint can be found in
the aws console following model deployment, and the dynamodb table name was set in step 4.
    ```
    REDDIT_CLIENT_ID = your_client_id
    REDDIT_CLIENT_SECRET = your_secret_id
    REDDIT_USER_AGENT = your_user_agent
    KINESIS_STREAM_NAME = your_stream_name
    DYNAMODB_TABLE_NAME = your_table_name
    AWS_REGION = your_region
    SAGEMAKER_ENDPOINT_NAME = your_endpoint_name
    MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
    ```

7. Start the Kinesis Stream and Run the Dash Application
    
    Navigate back to the project root directory, then:

    To start the Kinesis stream:
    ```
    python3 main.py
    ```

    Finally, to run the Dash application:

    ```
    python3 src/visualization/application.py
    ```
    Open your web browswer and navigate to `http://localhost:8050` to view the dashboard.

## Usage

Once the application and Kinesis stream are running, navigating to `http://localhost:8050` in a 
web browser will show the dashboard. Using the controls on the left side, you can filter by team,
adjust the time window, or adjust the visualization properties. 

### Testing:

Once the application is set up, it's reccomended to run the included unit tests. These tests use
moto to mock-test aws components. The tests cover the following modules:

<ul>
    <li><strong>Sagemaker:</strong> Tests to verify that the model is correctly invoked and returns
    expected sentiment scores
    <li><strong>Data Processing Logic:</strong> Tests verify that data is ingested and processed 
    correctly, checking data transformations and storage.
</ul>

To run the tests, execute the following command from the project root directory:

```
pytest tests/
```

## Roadmap

- Extend sentiment analysis with more advanced analytics, such as sentiment correlation with
match outcomes or player performance.
- Incorporate additional data sources like Twitter
- Incorporate a database caching layer with Redis to improve efficiency of queries

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for new features, feel free to 
open an issue or submit a pull request.
