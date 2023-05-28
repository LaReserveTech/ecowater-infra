import mailjet_rest
from common import db_connection
from mailjet_rest import Client
import os

# lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']

credential = db_connection.get_credentials(SECRET_NAME, REGION_NAME, DB)


def lambda_handler(event, context):
#def send_email(destinataire,niveau):

    mailjet = Client(auth=(credential['mailjet_api_key'], credential['mailjet_api_secret']), version='v3.1')
    data = {
    'Messages': [
            {
                "From": {
                    "Email": "florian@alerte-secheresse.fr",
                    "Name": "Alerte Sécheresse"
                },
                "To": [
                    {
                        "Email": "",
                        "Name": "passenger 1"
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

    result = mailjet.send.create(data=data)
    print (result.status_code)
    print (result.json())

    return None
