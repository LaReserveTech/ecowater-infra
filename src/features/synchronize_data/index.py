import io
import os
import zipfile
import logging
import requests
import csv
from typing import Optional
from datetime import datetime
import traceback

import psycopg2
from psycopg2.extras import DictCursor
import geopandas
from shapely.geometry import MultiPolygon

# from common import connect_to_local_db # Local Docker database connection
import db_connection # Dev/Prod database connection
from data_provider import get_data
import geozone_repository
import repositories.decree_repository as decree_repository
import restriction_repository
from sync_report import SyncReport
from event_dispatcher import EventDispatcher
from geozone import Geozone
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
    cursor = connection.cursor(cursor_factory = DictCursor)

    logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Connected to the database')

    urls = get_data()
    event_dispatcher = EventDispatcher(cursor)
    synchronize_geozones(cursor, urls, event_dispatcher)
    synchronize_decrees(cursor, urls, event_dispatcher)
    synchronize_restrictions(cursor, urls, event_dispatcher)

    cursor.close()
    connection.close()

def get(url):
    '''gets csv from url and parse the data '''
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f'Request to {url} failed with error status {response.status_code}.')
        return None

    decoded_content = response.content.decode('utf-8')
    cr = csv.DictReader(decoded_content.splitlines(), delimiter = ',', quotechar='"')

    return list(cr)

def synchronize_geozones(cursor, urls: dict, event_dispatcher: EventDispatcher) -> None:
    logging.info(f"Starting geozones synchronization, url: {urls.get('geozones', 'None')}")

    if not urls.get('geozones'):
        logging.error(f"Geozones synchronization failed, missing url: {urls.get('geozones', 'None')}")

        return

    sync_report = SyncReport()
    filepaths = extract_geozone_files(urls, '/tmp')

    gdf = geopandas.read_file(filepaths.get('shape_file'), crs = filepaths.get('projection_file'))
    gdf = gdf.set_crs("EPSG:4326")

    for (_, row) in gdf.iterrows():
        try:
            external_id = row.get('id_zone')
            if external_id is None:
                logging.error('Failed to import decree, no external id provided.')
                sync_report.error_count += 1

                continue

            if row.get('type_zone') == 'SUP':
                type = 'surface_water'
            elif row.get('type_zone') == 'SOU':
                type = 'ground_water'
            else:
                logging.warning(f"Failed to import geozone, type not handled: Type: {row.get('type_zone')}, External ID: {row.get('id_zone', 'None')}.")

                continue

            if None == row.get('geometry'):
                logging.warning(f"Failed to import geozone, null geometry: External ID: {row.get('id_zone', 'None')}.")

                continue
            geometry = MultiPolygon([row.get('geometry')]).wkt if row.get('geometry').geom_type == 'Polygon' else row.get('geometry').wkt

            geozone = Geozone(
                id = None,
                type = type,
                name = row.get('nom_zone'),
                external_id = external_id,
                geometry = geometry,
            )

            existing_geozone = geozone_repository.find_by_external_id(cursor, geozone.external_id)
            if None == existing_geozone:
                geozone_id = geozone_repository.insert(cursor, geozone)
                sync_report.created_count += 1
                event_dispatcher.dispatch(Event.GEOZONE_CREATION, geozone_id, None)

                continue

            sync_report.unchanged_count += 1
        except Exception as e:
            logging.error(f"Failed to import geozone: External ID: {row.get('id_zone', 'None')}. Exception: {str(e)}, Traceback: {traceback.print_exc()}")
            sync_report.error_count += 1

    logging.info(f"End of geozones synchronization. {sync_report}")

def synchronize_decrees(cursor, urls: dict, event_dispatcher: EventDispatcher) -> None:
    logging.info(f"Starting decrees synchronization, url: {urls.get('decrees', 'None')}")

    if not urls.get('decrees'):
        logging.error(f"Decrees synchronization failed, missing url: {urls.get('decrees', 'None')}")

        return

    sync_report = SyncReport()
    decrees = get(urls.get('decrees'))

    for row in decrees:
        try:
            if not row.get('id_zone', None):
                logging.error('Failed to import decree, geozone external id missing. Geozone External ID: %s', row.get('id_zone', 'None'))
                sync_report.error_count += 1

                continue

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
                id = None,
                external_id = external_id,
                geozone_id = geozone.id,
                alert_level = row.get('nom_niveau').lower(),
                start_date = datetime.strptime(row.get('debut_validite_arrete'), '%Y-%m-%d').date(),
                end_date = datetime.strptime(row.get('fin_validite_arrete'), '%Y-%m-%d').date(),
                document = row.get('chemin_fichier'),
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
            logging.error(f"Failed to import decree: External ID: {row.get('unique_key_arrete_zone_alerte', 'None')}. Exception: {str(e)}, Traceback: {traceback.print_exc()}")
            sync_report.error_count += 1

    logging.info(f"End of decrees synchronization. {sync_report}")

def synchronize_restrictions(cursor, urls: dict, event_dispatcher: EventDispatcher) -> None:
    logging.info(f"Starting restrictions synchronization, url: {urls.get('restrictions', 'None')}")

    if not urls.get('restrictions'):
        logging.error(f"Restrictions synchronization failed, missing url: {urls.get('restrictions', 'None')}")

        return

    retrictions = get(urls.get('restrictions'))
    sync_report = SyncReport()

    for row in retrictions:
        try:
            if not row.get('unique_key_arrete_zone_alerte', None):
                logging.error('Failed to import restriction, decree external id missing. Deozone External ID: %s', row.get('unique_key_arrete_zone_alerte', 'None'))
                sync_report.error_count += 1

                continue

            decree = decree_repository.find_by_external_id(cursor, row.get('unique_key_arrete_zone_alerte'))
            if decree is None:
                logging.error('Failed to import restriction, decree not found. Decree External ID: %s', row.get('unique_key_arrete_zone_alerte', 'None'))
                sync_report.error_count += 1

                continue

            external_id = row.get('unique_key_arrete_zone_alerte') + row.get('unique_key_restriction_alerte')

            restriction = Restriction(
                id = None,
                external_id = external_id,
                decree_id = decree.id,
                restriction_level = row.get('nom_niveau_restriction'),
                user_individual = parse_restriction_user(row.get('concerne_particulier')),
                user_company = parse_restriction_user(row.get('concerne_entreprise')),
                user_community = parse_restriction_user(row.get('concerne_collectivite')),
                user_farming = parse_restriction_user(row.get('concerne_exploitation')),
                theme = row.get('nom_thematique'),
                label = row.get('nom_usage'),
                description = row.get('nom_usage_personnalise'),
                specification = row.get('niveau_alerte_restriction_texte'),
                from_hour = parse_restriction_time(row.get('heure_debut'), row.get('unique_key_restriction_alerte')),
                to_hour = parse_restriction_time(row.get('heure_fin'), row.get('unique_key_restriction_alerte')),
            )

            existing_restriction = restriction_repository.find_by_external_id(cursor, external_id)

            if None == existing_restriction:
                restriction_id = restriction_repository.insert(cursor, restriction)
                sync_report.created_count += 1
                event_dispatcher.dispatch(Event.RESTRICTION_CREATION, restriction_id, None)
            else:
                restriction.id = existing_restriction.id
                restriction_repository.update(cursor, restriction)
                sync_report.updated_count += 1
                event_dispatcher.dispatch(Event.RESTRICTION_MODIFICATION, restriction.id, None)
        except Exception as e:
            logging.error(f"Failed to import restriction (external ID: {external_id}). Exception: {str(e)}, Traceback: {traceback.print_exc()}")
            sync_report.error_count += 1

    logging.info(f"End of restrictions synchronization. {sync_report}")

def extract_geozone_files(urls: dict, extraction_path: str) -> dict:
    url = urls.get('geozones')
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f'Request to {url} failed with error status {response.status_code}.')

        return None

    zip_bytes = io.BytesIO(response.content)

    with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
        zip_ref.extractall(extraction_path)

    return {
        'shape_file': extraction_path + '/all_zones.shp',
        'projection_file': extraction_path + '/all_zones.prj'
    }

def parse_restriction_user(user: Optional[str]) -> bool:
    return True if None != user and user.lower() == "True" else False

def parse_restriction_time(time: str, restriction_external_id: str) -> Optional[int]:
    if not time or time.lower() == 'null':
        return None

    try:
        return int(float(time))
    except Exception as e:
        logging.warning(
            'Failed to parse time. Restriction External ID: %s, Time Value: %s, Exception: %s',
            'None' if not restriction_external_id else restriction_external_id,
            'None' if not time else time,
            str(e)
        )
        return None

if __name__ == '__main__':
    lambda_handler(None, None)
