import * as fs from "fs";
import { parse } from "csv-parse/sync";

const fetchDecreesHttp = async (): Promise<any> => {
  const urls = await fetch(
    "https://data.gouv.fr/api/1/datasets/6470b39cfbad66b8c265ada3",
  );
  const json = await urls.json();
  const decreeResource = json["resources"].filter(
    (resource) => "arrêtés" === resource.title.toLowerCase(),
  )[0];

  const decreesCsvContent = await (await fetch(decreeResource.url)).text();

  return parse(decreesCsvContent, {
    columns: true,
    skip_empty_lines: true,
  });
};

const fetchDecreesLocal = async (): Promise<any> => {
  const fileContent = await fs.promises.readFile("./data/arretes.csv", "utf-8");
  return parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
  });
};

export const fetchDecrees = (): Promise<any> => {
  if ("true" === process.env["FETCH_DATA_LOCAL"]) {
    return fetchDecreesLocal();
  }

  return fetchDecreesHttp();
};
