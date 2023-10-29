import "dotenv/config";
import { Handler } from "aws-lambda";
import { Client } from "pg";
import { fetchGeoJson } from "../utils/geojson-provider";

const synchronize: Handler = async (_event: any) => {
  console.log("Geozones synchronziation started");
  let client: any;

  try {
    client = new Client();
    await client.connect();
    console.log("Connected to the database");

    console.log("Fetching geojson");
    const geoJSON = await fetchGeoJson();
    console.log("Fetched geojson");

    for (const feature of geoJSON.features) {
      const geometry = feature.geometry;
      const properties = feature.properties;

      const query = `
        INSERT INTO geozone (external_id, type, name, geometry)
        VALUES ($1, $2, $3, ST_GeomFromGeoJSON($4))
        ON CONFLICT (external_id) DO UPDATE
        SET type = EXCLUDED.type, name = EXCLUDED.name, geometry = EXCLUDED.geometry;
      `;

      await client.query(query, [
        properties["id_zone"],
        properties["type_zone"],
        properties["nom_zone"],
        geometry,
      ]);
    }

    console.log("Geojson synchronization successfull");
  } catch (error) {
    console.error(error);
  } finally {
    !!client && (await client.end());
    console.log("Closed connection to the database");
  }
};

export default synchronize;
