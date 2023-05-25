import os
import logging
import getCredentials_layer as gc
import psycopg2
import datetime

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

subscribtion_date = f"{datetime.datetime.now():%Y-%m-%d}"

logging.getLogger().setLevel(logging.DEBUG)

#Connect to the database
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)

connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
logging.debug("Connected to the database")

#Insert email into the database
def lambda_handler(event, context):
    if event['rawPath'] == RAW_PATH:
      #Get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      email = event['queryStringParameters']['email']

      if longitude is None:
        logging.error("Parameter validation : longitude is missing")
        return {
          "statusCode": "422",
          "body": "Unprocessable Entity : longitude is missing"
        }
      
      elif latitude is None:
        logging.error("Parameter validation : latitude is missing")
        return {
          "statusCode": "422",
          "body": "Unprocessable Entity : latitude is missing"
        } 

      elif email is None:
        logging.error("Parameter validation : email is missing")
        return {
          "statusCode": "422",
          "body": "Unprocessable Entity : email is missing"
        }
      else:
        logging.debug("Parameter validation : OK")

      query = 'INSERT into alert_subscription (email, longitude, latitude, subscribed_at) VALUES (%s, %s, %s,  %s);'
      parameters = (email, longitude, latitude, subscribtion_date)

      try:
        cursor = connection.cursor()
        cursor.execute(query, parameters)

        cursor.close()
        connection.commit()

        logging.debug("Email successfully registered in the DB")

        return {
          "statusCode": "202",
          "body": "Email successfully registered in the DB"
        }     

      except Exception as exeption:
        print("Error: ", exeption)

    else:
      return {"Error" : "Wrong API path"}
