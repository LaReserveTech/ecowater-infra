import * as fs from "fs";
import * as zlib from "zlib";

const fetchGeoJsonHttp = async (): Promise<any> => {
  const urls = await fetch(
    "https://data.gouv.fr/api/1/datasets/6470b39cfbad66b8c265ada3",
  );
  const json = await urls.json();
  const geoJsonUrl = json["resources"].filter(
    (resource) => "geojson" === resource.format,
  )[0];
  const geoJsonGzContent = await fetch(geoJsonUrl.url);
  const geoJsonGz = await geoJsonGzContent.arrayBuffer();

  return JSON.parse(zlib.gunzipSync(geoJsonGz).toString());
};

const fetchGeoJsonLocal = async (): Promise<any> => {
  const fileContent = await fs.promises.readFile(
    "./data/zones_arretes_en_vigueur.geojson",
    "utf-8",
  );

  return JSON.parse(fileContent);
};

export const fetchGeoJson = (): Promise<any> => {
  if ("true" === process.env["FETCH_DATA_LOCAL"]) {
    return fetchGeoJsonLocal();
  }

  return fetchGeoJsonHttp();
};
