import os
import logging
import requests
import csv
from typing import Optional
from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor

# from common import connect_to_local_db # Local Docker database connection
import db_connection # Dev/Prod database connection
from data_provider import get_data
import geozone_repository
import decree_repository
import restriction_repository
from sync_report import SyncReport
from event_dispatcher import EventDispatcher
from decree import Decree
from restriction import Restriction
from event import Event

# lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']

def lambda_handler(_event, _context):
    connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB)

    connection.autocommit = True
    cursor = connection.cursor(cursor_factory=DictCursor)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Connected to the database')

    urls = get_data()
    event_dispatcher = EventDispatcher(cursor)
    synchronize_decrees(cursor, urls, event_dispatcher)
    synchronize_restrictions(cursor, urls)

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

def synchronize_decrees(cursor, urls, event_dispatcher: EventDispatcher) -> None:
    logging.info(f"Starting decrees synchronization, url: {urls.get('decrees', 'None')}")

    if not urls.get('decrees'):
        logging.error(f"Decrees synchronization failed, missing url: {urls.get('decrees', 'None')}")

        return

    decrees = get(urls.get('decrees'))
    sync_report = SyncReport()

    for row in decrees:
        try:
            geozone = geozone_repository.find_by_external_id(cursor, row.get('id_zone', None))
            if geozone is None:
                logging.error('Failed to import decree, geozone not found. Geozone External ID: %s', row.get('id_zone', 'None'))
                sync_report.error_count += 1

                continue

            external_id = row.get('unique_key_arrete_zone_alerte')
            if external_id is None:
                logging.error('Failed to import decree, no external id provided.')
                sync_report.error_count += 1

                continue

            decree = Decree(
                None,
                row.get('unique_key_arrete_zone_alerte'),
                geozone.get('id'),
                row.get('nom_niveau').lower(),
                datetime.strptime(row.get('debut_validite_arrete'), '%Y-%m-%d').date(),
                datetime.strptime(row.get('fin_validite_arrete'), '%Y-%m-%d').date(),
                row.get('chemin_fichier')
            )

            existing_decree = decree_repository.find_by_external_id(cursor, decree.external_id)

            if None == existing_decree:
                decree_id = decree_repository.insert(cursor, decree)
                sync_report.created_count += 1
                event_dispatcher.dispatch(Event.DECREE_CREATION, decree_id, None)

                continue

            if decree.end_date != existing_decree.end_date:
                existing_decree.repeal(decree.end_date)
                decree_repository.update(cursor, existing_decree)
                sync_report.updated_count += 1
                event_dispatcher.dispatch(Event.DECREE_REPEAL, existing_decree.id, None)

                continue

            if decree.alert_level != existing_decree.alert_level:
                logging.warning(f"Decree alert level has been modified but ignored. ID: {existing_decree.id}, External ID: {existing_decree.external_id}, Persisted Alert Level: {existing_decree.alert_level}, Incomming Alert Level: {decree.alert_level}")

            if decree.geozone_id != existing_decree.geozone_id:
                logging.warning(f"Decree geozone has been modified but ignored. ID: {existing_decree.id}, External ID: {existing_decree.external_id}, Persisted Geozone ID: {existing_decree.geozone_id}, Incomming Geozone ID: {decree.geozone_id}")

            sync_report.unchanged_count += 1

        except Exception as e:
            logging.error(f"Failed to import decree: External ID: {row.get('unique_key_arrete_zone_alerte', 'None')}. Exception: {str(e)}")
            sync_report.error_count += 1

    logging.info(f"End of decrees synchronization. {sync_report}")

def synchronize_restrictions(cursor, urls) -> None:
    logging.info(f"Starting restrictions synchronization, url: {urls.get('restrictions', 'None')}")

    if not urls.get('restrictions'):
        logging.error(f"Restrictions synchronization failed, missing url: {urls.get('restrictions', 'None')}")

        return

    retrictions = get(urls.get('restrictions'))
    sync_report = SyncReport()

    for row in retrictions:
        try:
            decree = decree_repository.find_by_external_id(cursor, row.get('unique_key_arrete_zone_alerte'))
            if decree is None:
                logging.error('Failed to import restriction, decree not found. Decree External ID: %s', row.get('unique_key_arrete_zone_alerte', 'None'))
                sync_report.error_count += 1

                continue

            external_id = row.get('unique_key_arrete_zone_alerte') + row.get('unique_key_restriction_alerte')

            restriction = Restriction(
                None,
                external_id,
                decree.id,
                row.get('nom_niveau_restriction'),
                parse_restriction_user(row.get('concerne_particulier')),
                parse_restriction_user(row.get('concerne_entreprise')),
                parse_restriction_user(row.get('concerne_collectivite')),
                parse_restriction_user(row.get('concerne_exploitation')),
                row.get('nom_thematique'),
                row.get('nom_usage'),
                row.get('nom_usage_personnalise'),
                row.get('niveau_alerte_restriction_texte'),
                parse_restriction_time(row.get('heure_debut'), row.get('unique_key_restriction_alerte')),
                parse_restriction_time(row.get('heure_fin'), row.get('unique_key_restriction_alerte')),
            )

            restriction_repository.save(cursor, restriction) # TODO replace `restriction_repository.save()` by 2 methods: one for creation and another for update
            sync_report.updated_count += 1

        except Exception as e:
            logging.error(f"Failed to import restriction (external ID: {external_id}). Exception: {str(e)}")
            sync_report.error_count += 1

    logging.info(f"End of restrictions synchronization. {sync_report}")

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
