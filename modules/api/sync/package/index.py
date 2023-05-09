import psycopg2
import logging
import datetime
import csv
import geozone_repository
import decree_provider
import decree_repository
import restriction_provider
import restriction_repository

def lambda_handler(_event, _context):
    connection = psycopg2.connect(database="ecowater", user="ecowater", password="ecowater", host="pg", port="5432") # TODO use environment variables
    connection.autocommit = True
    cursor = connection.cursor()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('Connected to the database')

    # Decrees
    decrees_content = decree_provider.get()
    decrees_rows = csv.DictReader(decrees_content.splitlines(), delimiter=',')

    for row in decrees_rows:
        try:
            geozone = geozone_repository.find_by_external_id(cursor, row['CodeZA'])
            start_date_month, start_date_day, start_date_year = row['Date_Debut'].split('/')
            start_date = datetime.date(int(start_date_year), int(start_date_month), int(start_date_day))
            end_date_month, end_date_day, end_date_year = row['Date_Fin'].split('/')
            end_date = datetime.date(int(end_date_year), int(end_date_month), int(end_date_day))
            decree_repository.save(cursor, row['Id'], geozone[0], row['Niveau_Alerte'].lower(), start_date, end_date)
        except Exception as e:
            logging.error('Failed to import decree: External ID: %s. Exception: %s', row.get('Id', 'None'), str(e))

    del decrees_content
    del decrees_rows

    # Restrictions
    restrictions_content = restriction_provider.get()
    restrictions_rows = csv.DictReader(restrictions_content.splitlines(), delimiter=',')

    restriction_repository.wipe(cursor) # TODO find a better way to handle upsert for restrictions

    for row in restrictions_rows:
        try:
            decree = decree_repository.find_by_external_id(cursor, row['ArreteId'])

            if decree is None:
                logging.error('Failed to import restriction, decree not found. Decree ID: %s', row.get('ArreteId', 'None'))
                continue

            try:
                from_hour = int(row['Heure_Debut'])
            except ValueError:
                from_hour = None

            try:
                to_hour = int(row['Heure_Fin'])
            except ValueError:
                to_hour = None

            user_individual = True if row['Particulier'].lower() == "oui" else False
            user_company = True if row['Entreprise'].lower() == "oui" else False
            user_community = True if row['Collectivite'].lower() == "oui" else False
            user_farming = True if row['Exploitation'].lower() == "oui" else False

            restriction_repository.save(cursor, decree[0], row['Niveau'].lower(), user_individual, user_company, user_community, user_farming, row['Thematique'], row['Nom_Usage'], row['Nom_Usage_Personalise'], row['Precision'], from_hour, to_hour)
        except Exception as e:
            logging.error('Failed to import restriction. Exception: %s', str(e))

    cursor.close()
    connection.close()

if __name__ == '__main__':
    lambda_handler(None, None)
