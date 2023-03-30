import os
import boto3
import json
import psycopg2

RAW_PATH = "/dev/which-zone"

#Lambda environment variables
ENVIRONMENT = os.environ['environment']

#Get the DB credentials from Secrets Manager
def getCredentials():
    credential = {}
    
    secret_name = "ecowater-dev"
    region_name = "eu-west-3"
    
    client = boto3.client(
      service_name='secretsmanager',
      region_name=region_name
    )
    
    get_secret_value_response = client.get_secret_value(
      SecretId=secret_name
    )
    
    secret = json.loads(get_secret_value_response['SecretString'])
    username = list(secret.keys())[1]
    
    credential['username'] = username
    credential['password'] = secret[username]
    credential['host'] = "ecowater-dev.c0t3flx8invj.eu-west-3.rds.amazonaws.com"
    credential['db'] = "ecowaterdev"
    
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