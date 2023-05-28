from typing import Optional
from datetime import datetime
from common import connect_to_local_db, db_connection
import logging
import requests
import csv

from data_provider import get_data
import geozone_repository
import decree_repository
import restriction_repository
import os

# lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']

def lambda_handler(_event, _context):
    # connect to database
    connection = db_connection.connect_to_db()
    # connection = connect_to_local_db()

    connection.autocommit = True
    cursor = connection.cursor()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Connected to the database')

    urls = get_data()

    synchronize_decrees(cursor, urls['decrees'])
    synchronize_restrictions(cursor, urls['restrictions'])

    cursor.close()
    connection.close()

def get(url):
    '''gets csv from url and parse the data '''
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f'Request to {url} failed with error status {response.status_code}.')
        return None

    decoded_content = response.content.decode('utf-8')

    cr = csv.DictReader(decoded_content.splitlines(), delimiter=',')
    return list(cr)

def synchronize_decrees(cursor, url_decrees) -> None:
    logging.info('Starting decrees synchronization')
    decrees = get(url_decrees)
    decrees_count, errors_count = 0, 0

    for row in decrees:
        try:
            geozone = geozone_repository.find_by_external_id(cursor, row.get('id_zone', None))

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
            decrees_count += 1
        except Exception as e:
            logging.error(f"Failed to import decree: External ID: {row.get('unique_key_arrete_zone_alerte', 'None')}. Exception: {str(e)}")
            errors_count += 1

    logging.info(f"End of decrees synchronization: {decrees_count} created, {errors_count} errors")

def synchronize_restrictions(cursor, url_restrictions) -> None:
    logging.info('Starting restrictions synchronization')

    retrictions = get(url_restrictions)
    restrictions_count, errors_count = 0, 0

    for row in retrictions:
        try:
            decree = decree_repository.find_by_external_id(cursor, row.get('unique_key_arrete_zone_alerte'))
            if decree is None:
                logging.error('Failed to import restriction, decree not found. Decree External ID: %s', row.get('unique_key_arrete_zone_alerte', 'None'))
                errors_count += 1
                continue

            external_id = row.get('unique_key_arrete_zone_alerte') + row.get('unique_key_restriction_alerte')
            restriction = {
                'external_id': external_id,
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
            restrictions_count += 1

        except Exception as e:
            logging.error(f"Failed to import restriction (external ID: {external_id}). Exception: {str(e)}")
            errors_count += 1


    # del restrictions_content
    # del restrictions_rows
    logging.info(f"End of restrictions synchronization: {restrictions_count} created, {errors_count} errors")

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