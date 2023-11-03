import { LightRestriction } from "../handlers/get-area-data";

export default function formatRestrictions(restrictions: LightRestriction[]) {
  if (!restrictions.length) return {};

  return restrictions.reduce(
    (result, restriction) => {
      const formattedRestriction = {
        thematique: restriction.theme,
        "libelle-personnalise":
          restriction.description !== "" ? restriction.description : undefined,
        "en-savoir-plus": restriction.specification,
      };

      switch (restriction.restriction_level) {
        case "Sensibilisation":
          result["sensibilisation"][restriction.label] = formattedRestriction;
          break;
        case "Réduction de prélèvement":
          result["reduction-prelevement"][restriction.label] =
            formattedRestriction;
          break;
        case "Interdiction sur plage horaire":
          result["interdiction-plage-horaire"][restriction.label] = {
            thematique: restriction.theme,
            "heure-debut": restriction.from_hour,
            "heure-fin": restriction.to_hour,
            "en-savoir-plus": restriction.specification,
          };
          break;
        case "Interdiction sauf exception":
          result["interdiction-sauf-exception"][restriction.label] =
            formattedRestriction;
          break;
        case "Interdiction":
          result["interdiction"][restriction.label] = formattedRestriction;
          break;
        default:
          break;
      }
      return result;
    },
    {
      sensibilisation: {},
      "reduction-prelevement": {},
      "interdiction-plage-horaire": {},
      "interdiction-sauf-exception": {},
      interdiction: {},
    },
  );
}
