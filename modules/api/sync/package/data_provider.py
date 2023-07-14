import requests
import json
import logging

# url = 'https://demo.data.gouv.fr/api/1/datasets/643d5f985c230e2b786c5602'
url = 'https://data.gouv.fr/api/1/datasets/6470b39cfbad66b8c265ada3'

def get_data():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f'Request failed. status code: {response.status_code}, body: {response.content}')

        return

    data = json.loads(response.text)
    resources = data['resources']
    urls = {'restictions_url': None, 'decrees_url': None, 'geozones': None}

    for resource in resources:
        title = resource['title']

        if 'Restriction' in title:
            urls['restictions_url'] = resource['url']
        if 'Arrêtés' == title:
            urls['decrees_url'] = resource['url']
        if 'Géométrie des zones' in title:
            urls['geozones'] = resource['url']

    return urls

if __name__ == '__main__':
    get_data()
