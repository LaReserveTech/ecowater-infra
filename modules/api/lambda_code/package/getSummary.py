from data_provider import get_mocked_restrictions

def create_summary(restrictions_data):
  restrictions_dict = {
    "sensibilisation": {},
    "reduction-prelevement": {},
    "interdiction-plage-horaire": {},
    "interdiction-sauf-exception": {},
    "interdiction": {},
  }

  for item in restrictions_data:
    formatted_restriction = {
      "thematique": item[2],
      "libelle-personnalise": item[6],
      "en-savoir-plus": item[5],
    }

    if item[1] == "Sensibilisation":
      restrictions_dict["sensibilisation"][item[3]] = formatted_restriction

    elif item[1] == "Réduction de prélèvement":
      restrictions_dict["reduction-prelevement"][item[3]] = formatted_restriction

    elif item[1] == "Interdiction sur plage horaire":
      restrictions_dict["interdiction-plage-horaire"][item[3]] = {
        "thematique": item[2],
        "heure-debut": item[6],
        "heure-fin": item[7],
        "en-savoir-plus": item[5],
      }

    elif item[1] == "Interdiction sauf exception":
      restrictions_dict["interdiction-sauf-exception"][item[3]] = formatted_restriction

    elif item[1] == "Interdiction":
      restrictions_dict["interdiction"][item[3]] = formatted_restriction

  result_dict = {
    "niveau-alerte": restrictions_data[0][0],
    "pdf": "dummy-pdf.fr",
    "restrictions": restrictions_dict
  }

  return result_dict


if __name__ == '__main__':
  create_summary(get_mocked_restrictions())
