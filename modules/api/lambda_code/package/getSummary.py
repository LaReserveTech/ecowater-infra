from data_provider import get_mocked_restrictions

def create_summary(restrictions_data):
  results_dict = {
    "sensibilisation": {},
    "reduction-prelevement": {},
    "interdiction-plage-horaire": {},
    "interdiction-sauf-exception": {},
    "interdiction": {},
  }

  # useful to understand how the data is structured
  dict_by_level_restriction = {
    "Sensibilisation": [],
    "Réduction de prélèvement": [],
    "Interdiction sur plage horaire": [],
    "Interdiction sauf exception": [],
    "Interdiction": []
  }
  
  for item in restrictions_data:
    results_dict["niveau-alerte"] = item[0] # need to check if this is the expected behaviour

    formatted_restriction = {
        "thematique": item[2],
        "libelle-personnalise": item[6],
        "en-savoir-plus": item[5],
    }

    if item[1] == "Sensibilisation":
        dict_by_level_restriction["Sensibilisation"].append(item)
        results_dict["sensibilisation"][item[3]] = formatted_restriction

    elif item[1] == "Réduction de prélèvement":
        dict_by_level_restriction["Réduction de prélèvement"].append(item)
        results_dict["reduction-prelevement"][item[3]] = formatted_restriction
    
    elif item[1] == "Interdiction sur plage horaire":
        dict_by_level_restriction["Interdiction sur plage horaire"].append(item)
        results_dict["interdiction-plage-horaire"][item[3]] = {
            "thematique": item[2],
            "heure-debut": item[6],
            "heure-fin": item[7],
            "en-savoir-plus": item[5],
        }

    elif item[1] == "Interdiction sauf exception":
        dict_by_level_restriction["Interdiction sauf exception"].append(item)
        results_dict["interdiction-sauf-exception"][item[3]] = formatted_restriction

    elif item[1] == "Interdiction":
        dict_by_level_restriction["Interdiction"].append(item)
        results_dict["interdiction"][item[3]] = formatted_restriction

  print(results_dict)

  return results_dict


    
if __name__ == '__main__':
  create_summary(get_mocked_restrictions())