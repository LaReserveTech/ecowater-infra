from typing import Optional
from datetime import datetime
import psycopg2
import logging
import csv
import data_provider
import geozone_repository
import decree_provider
import decree_repository
import restriction_provider
import restriction_repository
import os
import getCredentials_layer as gc

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']

def lambda_handler(_event, _context):
    #connection = psycopg2.connect(database="ecowater", user="ecowater", password="ecowater", host="pg", port="5432") # TODO use environment variables
    #connection.autocommit = True
    #cursor = connection.cursor()
    
    #Connect to the database
    credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)
          
    connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
    connection.autocommit = True
    cursor = connection.cursor()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Connected to the database')

    #data_provider.get_data()
    # todo replace the existing file reader by the file getted by the previous function

    synchronize_decrees(cursor)
    synchronize_restrictions(cursor)

    cursor.close()
    connection.close()

def synchronize_decrees(cursor) -> None:
    logging.info('Starting decrees synchronization')
    decrees_content = decree_provider.get()
    decrees_rows = csv.DictReader(decrees_content.splitlines(), delimiter=',')

    for row in decrees_rows:
        try:
            geozone = geozone_repository.find_by_external_id(cursor, row['id_zone'])

            if geozone is None:
                logging.error('Failed to import decree, geozone not found. Geozone External ID: %s', row.get('id_zone', 'None'))
                continue

            decree = {
                'external_id': row.get('unique_key_arrete_zone_alerte'),
                'geozone_id': geozone[0],
                'start_date': datetime.strptime(row.get('debut_validite_arrete'), '%Y-%m-%d'),
                'end_date': datetime.strptime(row.get('fin_validite_arrete'), '%Y-%m-%d'),
                'alert_level': row.get('nom_niveau').lower(),
            }
            decree_repository.save(cursor, decree)
        except Exception as e:
            logging.error('Failed to import decree: External ID: %s. Exception: %s', row.get('unique_key_arrete_zone_alerte', 'None'), str(e))

    del decrees_content
    del decrees_rows
    logging.info('End of decrees synchronization')

def synchronize_restrictions(cursor) -> None:
    logging.info('Starting restrictions synchronization')
    restrictions_content = restriction_provider.get()
    restrictions_rows = csv.DictReader(restrictions_content.splitlines(), delimiter=',')

    for row in restrictions_rows:
        try:
            decree = decree_repository.find_by_external_id(cursor, row.get('unique_key_arrete_zone_alerte'))

            if decree is None:
                logging.error('Failed to import restriction, decree not found. Decree External ID: %s', row.get('unique_key_arrete_zone_alerte', 'None'))
                continue

            restriction = {
                'external_id': row.get('unique_key_arrete_zone_alerte') + row.get('unique_key_restriction_alerte'),
                'decree_id': decree[0],
                'restriction_level': row.get('nom_niveau_restriction'),
                'user_individual': parse_restriction_user(row.get('concerne_particulier')),
                'user_company': parse_restriction_user(row.get('concerne_entreprise')),
                'user_community': parse_restriction_user(row.get('concerne_collectivite')),
                'user_farming': parse_restriction_user(row.get('concerne_exploitation')),
                'theme': row.get('nom_thematique'),
                'label': row.get('nom_usage'),
                'description': row.get('nom_usage_personnalise'),
                'specification': row.get('niveau_alerte_restriction_texte'),
                'from_hour': parse_restriction_time(row.get('heure_debut'), row.get('unique_key_restriction_alerte')),
                'to_hour': parse_restriction_time(row.get('heure_fin'), row.get('unique_key_restriction_alerte')),
            }

            restriction_repository.save(cursor, restriction)
        except Exception as e:
            logging.error('Failed to import restriction. Exception: %s', str(e))

    del restrictions_content
    del restrictions_rows
    logging.info('End of restrictions synchronization')

def parse_restriction_user(user) -> bool:
    return True if user.lower() == "true" else False

def parse_restriction_time(time: str, restriction_external_id: str) -> Optional[int]:
    if time.lower() == 'null':
        return None

    try:
        return int(time)
    except Exception as e:
        logging.warning(
            'Failed to parse `from_hour` column. Restriction External ID: %s, From Hour Value: %s, Exception: %s',
            'None' if restriction_external_id is None or restriction_external_id == "" else restriction_external_id,
            'None' if time is None or time == "" else time,
            str(e)
        )
        return None

if __name__ == '__main__':
    lambda_handler(None, None)