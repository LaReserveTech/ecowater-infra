import os
import logging
import getCredentials_layer as gc
import psycopg2
from psycopg2.extensions import AsIs

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

#logging.getLogger().setLevel(logging.DEBUG)

#Connect to the database
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)
      
connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
connection.autocommit = True
logging.debug("Connected to the database")

#Query the database
def lambda_handler(event, context):
    if event['rawPath'] == RAW_PATH:
      #Get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      situation = event['queryStringParameters']['situation']

      query = """
      SELECT de.alert_level, re.restriction_level, re.theme, re.label, re.description, re.specification, re.from_hour, re.to_hour                                        
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
        results = cursor.fetchall()
        print (connection.encoding)
        
        cursor.close()
        connection.commit()
            
        results_dict = {}
        
        #for restriction in restriction_level : 
          #base64.b64encode(restriction).decode('utf-8')
        
        #Append the dictionary with reordered values in order to transform it in a json file // to change when the json model si updated
        for item in results:
          results_dict["niveau-alerte"] = item[0]

          if item[1] == "Sensibilisation":
            results_dict["sensibilisation"] = item[1]

          elif item[1] == "Réduction de prélèvement":
            results_dict["reduction-prelevement"] = item[1]

          elif item[1] == "Interdiction sur plage horaire":
            if item[2] == "Arrosage":
              results_dict["arrosage-pelouses-massifs-fleuris"] = {
                "thematique": "arrosage",
                "heure-debut": item[6],
                "heure-fin": item[7],
              }

          elif item[1] == "Interdiction sauf exception":
            if item[2] == "Irrigation":
              results_dict["irrigation-localisée-cultures"] = {
                "thematique": "irrigation",
                "en-savoir-plus": item[5],
              }

          elif item[1] == "Interdiction":
            if item[2] == "Arrosage":
              results_dict["interdiction"] = {
                "arrosage-jardins-potagers": {
                  "thematique": "arrosage",
                  "libelle-personnalise": "interdiction d'arroser les jardins potagers",
                  "en-savoir-plus": item[5],
                }
              }

        logging.debug("Sending results")
        return results_dict
        
      except Exception as e:
        logging.error('Failed to fetch restrictions. User: %s, Longitude: %s, Latitude: %s, Exception: %s', situation, longitude, latitude, str(e))
      
    else:
      return {"Error" : "Wrong API path"}