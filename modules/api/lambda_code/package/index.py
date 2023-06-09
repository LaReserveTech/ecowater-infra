import os
import logging
import db_connection
from psycopg2.extensions import AsIs
from getSummary import create_summary

# Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']
ENV = os.environ['env']

# Connect to database. Keep out of lambda_handler for performance
read_replica = True if ENV == 'prod' else False
connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB, read_replica)
connection.autocommit = True
logging.debug("Connected to the database")

def lambda_handler(event, context):
    RAW_PATH = os.environ['raw_path']

    if event['rawPath'] == RAW_PATH:
      # get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      situation = event['queryStringParameters']['situation']

      query = """
      SELECT DISTINCT de.alert_level, re.restriction_level, re.theme, re.label, re.description, re.specification, re.from_hour, re.to_hour, de.document
      FROM geozone AS gz
      INNER JOIN decree AS de ON de.geozone_id = gz.id
      LEFT JOIN restriction AS re ON re.decree_id = de.id
      WHERE ST_Contains(
          gz.geom,
          ST_SetSRID(
                ST_MakePoint(%s, %s),
                4326
          )
      )
      AND de.start_date <= NOW()
      AND NOW() <= de.end_date;
      """
      params = (longitude, latitude)

      try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        connection.commit()
      except Exception as e:
        logging.error('Failed to fetch restrictions. User: %s, Longitude: %s, Latitude: %s, Exception: %s', situation, longitude, latitude, str(e))

      # create the summary from the data
      results_dict = create_summary(data) if len(data) > 0 else {}
      return results_dict

    else:
      return {"Error" : "Wrong API path"}
