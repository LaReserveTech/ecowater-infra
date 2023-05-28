import os
import logging
import datetime
from email_validator import validate_email, EmailNotValidError
from common import db_connection

# lambda environment variables
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


# Insert email into the database
def lambda_handler(event, context):
    connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB)
    RAW_PATH = os.environ['raw_path']

    if event['rawPath'] == RAW_PATH:

      #1/Validate content-type
      headers = event['headers']

      if headers.get('content-type') is None or headers.get('content-type') != "application/json":
        logging.error("Content-type wasn't in the headers, or was not of type 'application/json'")
        return {
            "statusCode": "400",
            "body": "Content-type should be 'application/json'"
        }

      #2/Validate parameters
      parameters = event['queryStringParameters']

      if parameters.get('longitude') is not None and parameters.get('latitude') is not None and parameters.get('email') is not None:
        try:
          if isinstance (float(parameters['longitude']), float) and isinstance (float(parameters['latitude']), float): #TODO Check long/lat format
            logging.debug("The parameters are valid")

          else:
            logging.error("Long and/or lat is not in decimal degrees (DD)")
            return {
                "statusCode": "422",
                "body": "Longitude and/or latitude is not of the correct format. Must be decimal degrees (DD)"
            }
        except Exception as exeption_params:
          logging.error("Parameters not validated. Exception: %s", str(exeption_params))

      else:
        logging.error("A parameter is missing")
        return {
            "statusCode": "400",
            "body": "A parameter is missing. Parameters should be 'longitude','latitude' and 'email'"
        }

      #Get the coordinates and email from the API query
      longitude = parameters['longitude']
      latitude = parameters['latitude']
      email = parameters['email']

      #3/Validate email & insert it into the DB
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