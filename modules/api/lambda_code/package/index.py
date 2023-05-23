import os
import sys
import base64
import getCredentials_layer as gc
import psycopg2
from psycopg2 import OperationalError, errorcodes, errors

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
RAW_PATH = os.environ['raw_path']

#Error handling
def print_psycopg2_exception(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()
    
    # get the line number when exception occured
    line_num = traceback.tb_lineno
    
    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    print ("\nextensions.Diagnostics:", err.diag)

    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")

#Connect to the database
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)
      
connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
connection.autocommit = True
print ("Successfully connected to DB")

#Query the database
def lambda_handler(event, context):
    if event['rawPath'] == RAW_PATH:
      #Get the coordinates from the API query
      longitude = event['queryStringParameters']['longitude']
      latitude = event['queryStringParameters']['latitude']
      situation = event['queryStringParameters']['situation']

      query = """
      SELECT de.id, de.alert_level, re.restriction_level, re.{user}, re.theme, re.label, re.description, re.specification, re.from_hour, re.to_hour                                        
      FROM geozone AS gz
      INNER JOIN decree AS de ON de.geozone_id = gz.id
      INNER JOIN restriction AS re ON re.decree_id = de.id
      WHERE ST_Contains(
          gz.geom,
          ST_SetSRID(
                ST_MakePoint({lon}, {lat}),
                4326
          )
      );
      """.format(user = situation,lon = longitude,lat = latitude)
      try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall() #Get the query result in var
        print (connection.encoding)
        cursor.close()
        connection.commit()

        #Filter out the rows where the given situation is "false" (ex : user_individual = false)      
        filtered_results = []
        for item in results:
          if not any(value is False for value in item):
            filtered_results.append(item)
            
        results_dict = {'niveau-alerte':'niveau'}
        #Add all the restriction types into a list in order to decode them in utf-8
        restriction_encoding = ["Réduction de prélèvement"] #TODO : find a way to query the rows with special characters
        
        #for restriction in restriction_level : 
          #base64.b64encode(restriction).decode('utf-8')
        
        #Append the dictionary with reordered values in order to transform it in a json file
        for item in filtered_results:
          results_dict["niveau-alerte"] = item[1]
          
          if item[2] == "Sensibilisation":
            results_dict["sensibilisation"] = item[2] #to change when the json model is updated
            continue
            
          #elif item[2] == restriction_encoding[1]:
            #results_dict["reduction-prelevement"] = item[2] #to change when the json model is updated
            #continue
          
          elif item[2] == "Interdiction sauf exception":
            results_dict["interdiction-sauf-exception"] = item[2] #to change when the json model is updated
            continue
            
          elif item[2] == "Interdiction sur plage horaire":
            results_dict["interdiction-plage-horaire"] = item[2] #to change when the json model is updated
            continue
            
          elif item[2] == "Interdiction":
            if item[4] == "Arrosage":
              results_dict["interdiction"] = {
                "arrosage-jardins-potagers": {
                  "thematique": "arrosage",
                  "libelle-personnalise":"interdiction d'arroser les jardins potagers",
                  "en-savoir-plus":"Interdiction d'arroser les jardins potagers."}
              } #to change when the json model is updated
              continue
            continue
            
          else:
            break

        #print ("Writing to file")

        # Create a json file with the results from the DB query
        #json_file = open("restrictions.json", "w")
        #json.dump(results_json, json_file, indent = 6)
        #json_file.close()

        print ("Sending results")

        return results_dict # TODO : correct encoding of the responses (the special characters like "é" don't show well)
      
      except OperationalError as err:
        # pass exception to function
        print_psycopg2_exception(err)
      
    else:
      return {"Error" : "Wrong API path"}