"""This module deploys a pretrained Hugging Face model to a SageMaker endpoint."""

import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel

try:
    role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client('iam')
    role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

print(f"sagemaker role arn: {role}")

hub = {
  'HF_MODEL_ID':'cardiffnlp/twitter-roberta-base-sentiment-latest', # model_id from hf.co/models
  'HF_TASK':'sentiment-analysis' # NLP task
}

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
   env=hub,
   role=role, # iam role with permissions to create an Endpoint
   transformers_version="4.37", # transformers version used
   pytorch_version="2.1", # pytorch version used
   py_version="py310", # python version of the DLC
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
   initial_instance_count=1,
   instance_type="ml.m5.xlarge"
)
