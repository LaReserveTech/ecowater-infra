import "dotenv/config";
import { Handler } from "aws-lambda";
import { Client } from "pg";
import formatRestrictions from "../utils/data-summary";

const PDF_URL = "https://propluvia-data.s3.gra.io.cloud.ovh.net/pdf/";

const RESTRICTION_LEVEL_NUMBERS = {
  vigilance: 1,
  alerte: 2,
  "alerte renforcée": 3,
  crise: 4,
};

type LightDecree = {
  id: number;
  alert_level: "vigilance" | "alerte" | "alerte renforcée" | "crise";
  document: string;
};

export type LightRestriction = {
  restriction_level:
    | ""
    | "Interdiction sur plage horaire"
    | "Pas de restriction"
    | "Interdiction"
    | "Interdiction sauf exception"
    | "Réduction de prélèvement"
    | "Sensibilisation";
  theme: string;
  label: string;
  description: string;
  specification: string;
  from_hour: number; // in hour
  to_hour: number; // in hour
};

type getAreaDataEvent = {
  queryStringParameters: {
    latitude: number;
    longitude: number;
    situation: string;
  };
};

const getAreaData: Handler = async (event: getAreaDataEvent) => {
  const client = new Client();
  await client.connect();
  console.log("Connected to the database");

  const {
    queryStringParameters: { latitude, longitude },
  } = event;

  let decree: LightDecree | undefined;
  let restrictions: LightRestriction[] = [];

  try {
    const decreeQuery = `
      SELECT DISTINCT de.id, de.alert_level, de.document
      FROM geozone AS gz
      INNER JOIN decree AS de ON de.geozone_id = gz.id
      WHERE ST_Contains(
        gz.geometry,
        ST_SetSRID(
              ST_MakePoint($1, $2),
              4326
        )
      )
      AND de.start_date <= NOW()
      AND NOW() <= de.end_date;
    `;
    const decrees = (await client.query(decreeQuery, [longitude, latitude]))
      .rows as LightDecree[];

    if (decrees.length > 0) {
      // Hypothese: only 1 decree actif by area at a time
      decree = decrees[0];
      const query = `
      SELECT DISTINCT restriction_level, theme, label, description, specification, from_hour, to_hour
      FROM restriction
      INNER JOIN decree ON restriction.decree_id = decree.id
      WHERE decree.id = $1;
    `;

      restrictions = (await client.query(query, [decree.id]))
        .rows as LightRestriction[];
    }
  } catch (error) {
    console.error(error);
  } finally {
    await client.end();
    console.log("Closed connection to the database");
  }

  if (!decree) {
    return {};
  }

  return {
    "niveau-alerte": decree.alert_level,
    "niveau-alerte-chiffre": RESTRICTION_LEVEL_NUMBERS[decree.alert_level],
    document: `${PDF_URL}${encodeURI(decree.document)}`,
    restrictions: formatRestrictions(restrictions),
  };
};

export default getAreaData;
