import psycopg2
import logging
import datetime
import csv
import decree_provider
import decree_repository
import restriction_provider
import restriction_repository

def lambda_handler(_event, _context):
    connection = psycopg2.connect(database="ecowater", user="ecowater", password="ecowater", host="pg", port="5432")
    connection.autocommit = True
    cursor = connection.cursor()
    logging.info('Connected to the database')

    # Decrees
    decrees_content = decree_provider.get()
    decrees_rows = csv.DictReader(decrees_content.splitlines(), delimiter=',')

    for row in decrees_rows:
        start_date_month, start_date_day, start_date_year = row['Date_Debut'].split('/')
        start_date = datetime.date(int(start_date_year), int(start_date_month), int(start_date_day))
        end_date_month, end_date_day, end_date_year = row['Date_Fin'].split('/')
        end_date = datetime.date(int(end_date_year), int(end_date_month), int(end_date_day))
        decree_repository.save(cursor, row['Id'], row['CodeZA'], row['Niveau_Alerte'].lower(), start_date, end_date)

    del decrees_content
    del decrees_rows

    # Restrictions
    restrictions_content = restriction_provider.get()
    restrictions_rows = csv.DictReader(restrictions_content.splitlines(), delimiter=',')

    for row in restrictions_rows:
        decree = decree_repository.find_by_external_id(row['ArreteId'])
        restriction_repository.save(cursor, decree['id'], row)

    cursor.close()
    connection.close()

if __name__ == '__main__':
    lambda_handler(None, None)
