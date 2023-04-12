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
cursor = connection.cursor()
print ("Successfully connected to DB")

#Query the database
def lambda_handler(event, context):
    if event['rawPath'] == RAW_PATH:
      #Get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']

      query = """
      SELECT zone, niveau, mesurespart
      FROM localites
      INNER JOIN arrete ON localites.id = arrete.zone
      WHERE ST_Intersects('POINT({} {})'::geography::geometry, wkb_geometry);
      """.format(longitude,latitude)
      try:
        cursor.execute(query)
        results = cursor.fetchone()
        #print (results[0])
        
        cursor.close()
        connection.commit()

        print ("Sending results")
        return results
      
      except Exception as exeption:
        print("Error: ", exeption)
      
    else:
      return {"Error" : "Wrong API path"}