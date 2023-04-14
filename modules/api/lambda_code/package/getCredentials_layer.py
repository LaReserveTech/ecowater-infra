import os
import boto3
from botocore.exceptions import ClientError
import json

#Get the DB credentials from Secrets Manager
def getCredentials(SECRET_NAME, REGION_NAME, DB):
    credential = {}

    client = boto3.client(
      service_name = 'secretsmanager',
      region_name = REGION_NAME
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
        SecretId=SECRET_NAME
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    
    secret = json.loads(get_secret_value_response['SecretString'])
    username = list(secret.keys())[1]
    host = list(secret.keys())[2]
    mailjet_api_key = list(secret.keys())[3]
    mailjet_api_secret = list(secret.keys())[4]
    
    credential['username'] = username
    credential['password'] = secret[username]
    credential['host'] = secret[host]
    credential['db'] = DB
    credential['mailjet_api_key'] = secret[mailjet_api_key]
    credential['mailjet_api_secret'] = secret[mailjet_api_secret]
    
    return credential