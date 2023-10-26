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

def lambda_handler(_event, _context):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    read_replica = True if ENV == 'prod' else False
    connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB, read_replica)
    connection.autocommit = True
    cursor = connection.cursor()
    logging.debug('Connected to the database')

    query = 'SELECT COUNT(alert_level), alert_level FROM decree de WHERE start_date <= NOW() AND NOW() <= end_date GROUP BY alert_level;'

    cursor.execute(query)
    count = cursor.fetchall()
    count_dict = {row[1].replace("é", "e"): row[0] for row in count}

    cursor.close()
    connection.close()

    return count_dict
