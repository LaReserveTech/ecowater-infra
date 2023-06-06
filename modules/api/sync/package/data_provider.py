import requests
import json
import logging

# URL de l'API à appeler
DATASET='643d5f985c230e2b786c5602'
url = 'https://demo.data.gouv.fr/api/1/datasets/' + DATASET

def get_data():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # requête pour récupérer la liste des ressources disponibles
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f'Request failed with error status {response.status_code}')
        return None

    data = json.loads(response.text)
    resources = data['resources']

    # extraction des urls pour récupérer les restrictions et les arrêtés
    restictions_url, decrees_url = '', ''
    for resource in resources:
        title = resource['title']
        if 'Restriction' in title:
            restictions_url = resource['url']
        if 'Arretes' in title:
            decrees_url = resource['url']

    return {
        'restrictions': restictions_url,
        'decrees': decrees_url,
    }

if __name__ == '__main__':
    get_data()
