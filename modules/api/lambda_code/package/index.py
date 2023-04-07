import os
import boto3
from botocore.exceptions import ClientError
import json
import psycopg2

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

#Get the DB credentials from Secrets Manager
def getCredentials():
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
    
    credential['username'] = username
    credential['password'] = secret[username]
    credential['host'] = secret[host]
    credential['db'] = DB
    
    return credential

#Connect to the database and query it    
def lambda_handler(event, context):
    if event['rawPath'] == RAW_PATH:
      #Get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      
      credential = getCredentials()
      
      connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
      cursor = connection.cursor()
      print ("Successfully connected to DB")
      
      query = "SELECT ogc_fid, id , type, libel , dpt FROM localites WHERE ST_Intersects('POINT({} {})'::geography::geometry, wkb_geometry);".format(longitude,latitude)
      cursor.execute(query)
      results = cursor.fetchone()
      print (results[0])
      
      cursor.close()
      connection.commit()
      
      return results
      
    else:
      return {"message" : "error"}