import os
import logging
import getCredentials_layer as gc
import psycopg2
from psycopg2.extensions import AsIs
from getSummary import create_summary

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

#Connect to the database
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)

connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
connection.autocommit = True
logging.debug("Connected to the database")

#Query the database
def lambda_handler(event, context):
    if event['rawPath'] != RAW_PATH:
      return {"Error" : "Wrong API path"}

    # get the coordinates from the API query
    longitude = event['queryStringParameters']['longitude']
    latitude = event['queryStringParameters']['latitude']
    situation = event['queryStringParameters']['situation']

    query = """
    SELECT DISTINCT de.alert_level, re.restriction_level, re.theme, re.label, re.description, re.specification, re.from_hour, re.to_hour
    FROM geozone AS gz
    INNER JOIN decree AS de ON de.geozone_id = gz.id
    INNER JOIN restriction AS re ON re.decree_id = de.id
    WHERE ST_Contains(
        gz.geom,
        ST_SetSRID(
              ST_MakePoint(%s, %s),
              4326
        )
    )
    AND re.%s IS TRUE;
    """
    params = (longitude, latitude, AsIs(situation))

    try:
      cursor = connection.cursor()
      cursor.execute(query, params)
      data = cursor.fetchall()

      cursor.close()
      connection.commit()
    except Exception as e:
      logging.error('Failed to fetch restrictions. User: %s, Longitude: %s, Latitude: %s, Exception: %s', situation, longitude, latitude, str(e))

    # create the summary from the data
    results_dict = create_summary(data)

    return results_dict
