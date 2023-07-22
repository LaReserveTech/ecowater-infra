import logging
from mailjet_rest import Client
import os
import psycopg2
from psycopg2.extras import DictCursor

import db_connection

import repositories


# lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']

# def connect_to_local_db():
#     connection = psycopg2.connect(database="ecowater", user="ecowater", password="ecowater", host="pg", port="5432")
#     return connection

# def get_credentials():
#     '''get the DB credentials from Secrets Manager'''
#     return {
#         'mailjet_api_key': 'find key on aws',
#         'mailjet_api_secret': 'find key on aws',
#     }

credential = db_connection.get_credentials(SECRET_NAME, REGION_NAME, DB)
# credential = get_credentials()

def create_email(email_address):
    return {
    'Messages': [
            {
                "From": {
                    "Email": "florian@alerte-secheresse.fr",
                    "Name": "Alerte Sécheresse"
                },
                "To": [
                    {
                        "Email": email_address,
                        "Name": email_address
                    }
                ],
                "TemplateID": 4732985,
                "TemplateLanguage": True,
                "Subject": "renforcée",
                "Variables": {
                    "niveau": "maximale"
                }
            }
        ]
    }


def lambda_handler(event, context):
    connection = db_connection.connect_to_db(SECRET_NAME, REGION_NAME, DB)
    # connection = connect_to_local_db()
    connection.autocommit = True
    cursor = connection.cursor(cursor_factory=DictCursor)

    mailjet = Client(auth=(credential['mailjet_api_key'], credential['mailjet_api_secret']), version='v3.1')

    # récupérer les events qui doivent être consommés
    events = repositories.find_all_events(cursor)

    if events != None:
        # pour chaque event
        for event in events:
            # on récupère le decree associé et sa geozone
            stream_id = event[1]
            decree = repositories.get_decree_by_id(cursor, stream_id)
            if decree == None:
                logging.error('Decree with id %s not found.', stream_id)
                continue

            # on récupère les utilisateurs associés aux zones
            geozone_id = decree.get_geozone_id()
            email_addresses = repositories.get_user_emails_by_geozone_id(cursor, geozone_id)

            if len(email_addresses) > 0:
                # on envoie les emails à chaque utilisateur
                for email_address in email_addresses:
                    email = create_email(email_address[0])
                    result = mailjet.send.create(data=email)
                    print(result.status_code)
                    print(result.json())

            # TODO: on supprime l'event

    return

if __name__ == '__main__':
    lambda_handler(None, None)
