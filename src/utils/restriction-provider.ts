import * as fs from "fs";
import { parse } from "csv-parse/sync";

const fetchRestrictionsHttp = async (): Promise<any> => {
  const urls = await fetch(
    "https://data.gouv.fr/api/1/datasets/6470b39cfbad66b8c265ada3"
  );
  const json = await urls.json();
  const restrictionResource = json["resources"].filter(
    (resource) => "restrictions" === resource.title.toLowerCase()
  )[0];

  const restrictionsCsvContent = await (await fetch(restrictionResource.url)).text();

  return parse(restrictionsCsvContent, {
    columns: true,
    skip_empty_lines: true,
  });
};

const fetchRestrictionsLocal = async (): Promise<any> => {
  const fileContent = await fs.promises.readFile("./data/restrictions.csv", "utf-8");

  return parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
  });
};

export const fetchRestrictions = (): Promise<any> => {
  if ("true" === process.env["FETCH_DATA_LOCAL"]) {
    return fetchRestrictionsLocal();
  }

  return fetchRestrictionsHttp();
};
