import os
import db_connection #Comment when testing in local machine
#from common import connect_to_local_db #For testing in local machine
import logging

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']
ENV = os.environ['env']
RAW_PATH = os.environ['raw_path']

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') # For debugging

# Connect to database. Keep out of lambda_handler for performance
read_replica = True if ENV == 'prod' else False
connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB, read_replica)
connection.autocommit = True

# connection = connect_to_local_db() #for local testing

def lambda_handler(_event, _context):
    
    query = 'SELECT COUNT(alert_level), alert_level FROM decree de WHERE start_date <= NOW() AND NOW() <= end_date GROUP BY alert_level;'
    
    cursor = connection.cursor()
    logging.debug('Connected to the database')

    cursor.execute(query)
    count = cursor.fetchall()

    cursor.close()
    connection.close()

    return count