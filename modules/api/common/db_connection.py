import psycopg2
import boto3
from botocore.exceptions import ClientError
import json
import logging

def get_credentials(SECRET_NAME, REGION_NAME, DB):
    '''get the DB credentials from Secrets Manager'''

    client = boto3.client(
      service_name = 'secretsmanager',
      region_name = REGION_NAME
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    username = list(secret.keys())[1]
    host = list(secret.keys())[2]
    mailjet_api_key = list(secret.keys())[3]
    mailjet_api_secret = list(secret.keys())[4]

    return {
        'username': username,
        'password': secret[username],
        'host': secret[host],
        'db': DB,
        'mailjet_api_key': secret[mailjet_api_key],
        'mailjet_api_secret': secret[mailjet_api_secret],
    }


def connect_to_db(SECRET_NAME, REGION_NAME, DB):
    '''connect to the database'''

    credential = get_credentials(SECRET_NAME, REGION_NAME, DB)
    connection = psycopg2.connect(
        user=credential['username'],
        password=credential['password'],
        host=credential['host'],
        database=credential['db']
    )
    logging.debug("Connected to the database")
    return connection