import "dotenv/config";
import { Handler } from "aws-lambda";
import { Client } from "pg";
import { fetchDecrees } from '../utils/decree-provider'

const synchronize: Handler = async (_event: any) => {
  console.log("Decrees synchronziation started");
  const client = new Client();
  await client.connect();
  console.log("Connected to the database");

  try {
    console.log("Fetching decrees");
    const decrees = await fetchDecrees();
    console.log("Fetched decrees");

    for (const decree of decrees) {
      if (decree['statut_arrete'] === 'Terminé') {
        continue;
      }

      const res = await client.query(
        "SELECT id FROM geozone WHERE external_id = $1",
        [decree["id_zone"]]
      );

      const geozoneId = res?.rows[0]?.id;
      if (!geozoneId) {
        console.warn(
          `Decree cannot be synchronized, missing geozone. Geozone ID: ${decree["id_zone"]}, External ID: ${decree["unique_key_arrete_zone_alerte"]}`
        );

        continue;
      }

      const query = `
        INSERT INTO decree (external_id, geozone_id, alert_level, start_date, end_date, document)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (external_id) DO UPDATE
        SET geozone_id = EXCLUDED.geozone_id, alert_level = EXCLUDED.alert_level, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, document = EXCLUDED.document;
      `;

      await client.query(query, [
        decree["unique_key_arrete_zone_alerte"],
        geozoneId,
        decree["nom_niveau"].toLowerCase(),
        decree["debut_validite_arrete"],
        decree["fin_validite_arrete"] || null,
        decree["chemin_fichier"],
      ]);
    }

    console.log("Decrees synchronization successfull");
  } catch (error) {
    console.error(error);
  } finally {
    await client.end();
    console.log("Closed connection to the database");
  }
};

export default synchronize;
