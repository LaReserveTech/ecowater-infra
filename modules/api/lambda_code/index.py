import os
import boto3
import json

#Lambda environment variables
ENVIRONMENT = os.environ['environment']


  
def lambda_handler(event, context):
    print("Hello this is a test")