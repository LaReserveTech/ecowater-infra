import os
import logging
import db_connection
from psycopg2.extensions import AsIs
from getSummary import create_summary

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']


def lambda_handler(event, context):
    connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB)
    RAW_PATH = os.environ['raw_path']

    if event['rawPath'] == RAW_PATH:
      # get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      situation = event['queryStringParameters']['situation']

      query = """
      SELECT DISTINCT de.alert_level, re.restriction_level, re.theme, re.label, re.description, re.specification, re.from_hour, re.to_hour
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
      AND re.%s IS TRUE
      AND de.start_date <= NOW()
      AND NOW() <= de.end_date;
      """
      params = (longitude, latitude, AsIs(situation))

      try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        print (connection.encoding)

        cursor.close()
        connection.commit()

        # for restriction in restriction_level :
          #base64.b64encode(restriction).decode('utf-8')

        # create the summary from the data
        results_dict = create_summary(data)

        return results_dict

      except Exception as e:
        logging.error('Failed to fetch restrictions. User: %s, Longitude: %s, Latitude: %s, Exception: %s', situation, longitude, latitude, str(e))

    else:
      return {"Error" : "Wrong API path"}
