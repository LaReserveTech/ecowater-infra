# import the mailjet wrapper
import mailjet_rest
import getCredentials_layer as gc
from mailjet_rest import Client
import os
import psycopg2

#export MJ_APIKEY_PUBLsIC='your api key'
#export MJ_APIKEY_PRIVATE='your api secret'

# Get your environment Mailjet keys
#API_KEY = os.environ['MJ_APIKEY_PUBLIC']
#API_SECRET = os.environ['MJ_APIKEY_PRIVATE']

#Lambda environment variables
SECRET_NAME = os.environ['secret_name']
REGION_NAME = os.environ['region_name']
DB = os.environ['db']


#mailjet = Client(auth=(API_KEY, API_SECRET))

#Connect to the database and also get the API keys for mailjet
credential = gc.getCredentials(SECRET_NAME, REGION_NAME, DB)
      
connection = psycopg2.connect(user=credential['username'], password=credential['password'], host=credential['host'], database=credential['db'])
print ("Successfully connected to DB")


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


#send_email( "","maximale")