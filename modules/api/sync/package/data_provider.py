import requests
import json
import os

DATASET='643d5f985c230e2b786c5602'

def get_data():
    # URL de l'API à appeler
    url = 'https://demo.data.gouv.fr/api/1/datasets/' + DATASET

    # Faire une requête GET pour récupérer le fichier
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        #print (response.content)
        data = json.loads(response.text)
        print( len(data['resources']))
        nbfile = len(data['resources'])
        for x in range(nbfile):
            print( data['resources'][x]['url'])
            file=data['resources'][x]['url']
            response = requests.get(file)
            if response.status_code == 200:
        # Enregistrer le fichier sur le disque dur
                save_path = '/tmp/'
                completeName = os.path.join(save_path, data['resources'][x]['title'])
                with open(completeName, 'wb') as f:
                    f.write(response.content)
                print('Le fichier a été téléchargé avec succès.')
            else:
        # Afficher un message d'erreur si la requête a échoué
                print('La requête a échoué avec le code d\'erreur', response.status_code)
    else:
        # Afficher un message d'erreur si la requête a échoué
        print('La requête a échoué avec le code d\'erreur', response.status_code)
    return None