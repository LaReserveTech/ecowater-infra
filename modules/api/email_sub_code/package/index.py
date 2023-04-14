import os
import getCredentials_layer as gc
import psycopg2

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

#Connect to the database
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)
      
connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
print ("Successfully connected to DB")

#Insert email into the database
def lambda_handler(event, context):
    if event['rawPath'] == RAW_PATH:
      #Get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      email = event['queryStringParameters']['email']

      query = """
      INSERT into contacts ({})
      """.format(email)
      try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        cursor.close()
        connection.commit()

        print ("Email successfully registered in the DB")
      
      except Exception as exeption:
        print("Error: ", exeption)
      
    else:
      return {"Error" : "Wrong API path"}
