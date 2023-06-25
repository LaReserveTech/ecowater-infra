import requests
import json
import logging

# URL de l'API à appeler en preprod sur demo.data.gouv
#DATASET='643d5f985c230e2b786c5602'
#url = 'https://demo.data.gouv.fr/api/1/datasets/' + DATASET


# URL de l'API à appeler en prod sur data.gouv
DATASET='6470b39cfbad66b8c265ada3'
url = 'https://data.gouv.fr/api/1/datasets/' + DATASET

def get_data():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f'Request failed. status code: {response.status_code}, body: {response.content}')

        return

    data = json.loads(response.text)
    resources = data['resources']

    restictions_url, decrees_url = None, None
    for resource in resources:
        title = resource['title']

        if 'Restriction' in title:
            restictions_url = resource['url']
        if 'Arrêtés' == title:
            decrees_url = resource['url']

    return {
        'decrees': decrees_url,
        'restrictions': restictions_url,
    }

if __name__ == '__main__':
    get_data()
