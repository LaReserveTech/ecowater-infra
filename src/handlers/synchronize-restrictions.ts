import "dotenv/config";
import { Handler } from "aws-lambda";
import { Client } from "pg";
import { fetchRestrictions } from "../utils/restriction-provider";

const synchronize: Handler = async () => {
  console.log("Restrictions synchronziation started");
  const client = new Client();
  await client.connect();
  console.log("Connected to the database");

  try {
    console.log("Fetching restrictions");
    const restrictions = await fetchRestrictions();
    console.log("Fetched restrictions");

    for (const restriction of restrictions) {
      const res = await client.query(
        "SELECT id FROM decree WHERE external_id = $1",
        [restriction["unique_key_arrete_zone_alerte"]],
      );

      const decreeId = res?.rows[0]?.id;
      if (!decreeId) {
        // console.warn(
        //   `Restriction cannot be synchronized, missing decree. Decree ID: ${restriction["unique_key_arrete_zone_alerte"]}, Restriction Decree ID: ${restriction["unique_key_restriction_alerte"]}`
        // );

        continue;
      }

      const query = `
        INSERT INTO restriction (
          external_id,
          decree_id,
          restriction_level,
          user_individual,
          user_company,
          user_community,
          user_farming,
          theme,
          label,
          description,
          specification,
          from_hour,
          to_hour
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        ON CONFLICT (external_id) DO UPDATE
        SET
          decree_id = EXCLUDED.decree_id,
          restriction_level = EXCLUDED.restriction_level,
          user_individual = EXCLUDED.user_individual,
          user_company = EXCLUDED.user_company,
          user_community = EXCLUDED.user_community,
          user_farming = EXCLUDED.user_farming,
          theme = EXCLUDED.theme,
          label = EXCLUDED.label,
          description = EXCLUDED.description,
          specification = EXCLUDED.specification,
          from_hour = EXCLUDED.from_hour,
          to_hour = EXCLUDED.to_hour
        ;
      `;

      const parsedFromHour = parseInt(restrictions["heure_debut"]);
      const fromHour = !Number.isNaN(parsedFromHour) ? parsedFromHour : null;
      const parsedToHour = parseInt(restrictions["heure_fin"]);
      const toHour = !Number.isNaN(parsedToHour) ? parsedToHour : null;

      await client.query(query, [
        restriction["unique_key_arrete_zone_alerte"] +
          restriction["unique_key_restriction_alerte"],
        decreeId,
        restriction["nom_niveau_restriction"],
        restriction["concerne_particulier"].toLowerCase() === "true",
        restriction["concerne_entreprise"].toLowerCase() === "true",
        restriction["concerne_collectivite"].toLowerCase() === "true",
        restriction["concerne_exploitation"].toLowerCase() === "true",
        restriction["nom_thematique"],
        restriction["nom_usage"],
        restriction["nom_usage_personnalise"],
        restriction["niveau_alerte_restriction_texte"],
        fromHour,
        toHour,
      ]);
    }

    console.log("Restrictions synchronization successfull");
  } catch (error) {
    console.error(error);
  } finally {
    await client.end();
    console.log("Closed connection to the database");
  }
};

export default synchronize;
