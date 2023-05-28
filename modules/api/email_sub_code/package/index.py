import os
import logging
import getCredentials_layer as gc
import psycopg2
import datetime
from email_validator import validate_email, EmailNotValidError

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

subscribtion_date = f"{datetime.datetime.now():%Y-%m-%d}"

#logging.getLogger().setLevel(logging.DEBUG)

def validate_emails(email):
  try:
    # Check that the email address is valid.
    emailinfo = validate_email(email, check_deliverability=True)
  
    # After this point, use only the normalized form of the email address, before going to a database query.
    email = emailinfo.normalized
    return True
  
  except EmailNotValidError as e:
    # The exception message is human-readable explanation of why it's
    # not a valid (or deliverable) email address.
    logging.error("Email not valid. Exception: %s", str(e))
    return False

#Connect to the database
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)

connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
connection.autocommit = True
logging.debug("Connected to the database")

#Insert email into the database
def lambda_handler(event, context):
  if event['rawPath'] == RAW_PATH:
    #Get the coordinates from the API query
    longitude = event['queryStringParameters']['longitude']
    latitude = event['queryStringParameters']['latitude']
    email = event['queryStringParameters']['email']

    if validate_emails(email):
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
        logging.error("Email not registered in the DB. Exception: %s", str(exeption))
        
    else:
      return {
          "statusCode": "422",
          "body": "Unprocessable Entity : email is not valid"
          } 

  else:
    return {"Error" : "Wrong API path"}
