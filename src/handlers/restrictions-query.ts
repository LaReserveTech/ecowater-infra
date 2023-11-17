import 'dotenv/config'
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda'
import { Client } from 'pg'

interface QueryParameters {
  latitude?: string
  longitude?: string
  situation?: string
}

interface ErrorOutput {
  type: string
  title: string
  errors: Error
}

interface Error {
  [error: string]: string
}

interface Output {
  alertLevel: string|null,
  alertLevelValue: number|null,
  document: string|null,
  restrictions: RestrictionOutput[]|null,
}

interface RestrictionOutput {
  slug: string,
  restrictionLevel: string,
  theme: string,
  label: string,
  description: string,
  specification: string,
  fromHour: number,
  toHour: number,
}

export default async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  let client: Client | undefined

  try {
    const { latitude, longitude, situation } = event.queryStringParameters || {}

    const errorOutput = validateQuery({ latitude, longitude, situation })
    if (typeof errorOutput !== 'undefined') {
      return {
        statusCode: 400,
        body: JSON.stringify(errorOutput),
      }
    }

    client = new Client()
    await client.connect()

    const query = `
      SELECT DISTINCT gz.type,
        de.alert_level as "alertLevel",
        de.document,
        re.restriction_level AS "restrictionLevel",
        re.theme,
        re.label,
        re.description,
        re.specification,
        re.from_hour AS "fromHour",
        re.to_hour AS "toHour"
      FROM geozone AS gz
      INNER JOIN decree AS de ON de.geozone_id = gz.id
      LEFT JOIN restriction AS re ON re.decree_id = de.id
      WHERE ST_Contains(
        gz.geometry,
        ST_SetSRID(
          ST_MakePoint($1, $2),
          4326
        )
      )
      AND de.start_date <= NOW() AND de.end_date >= NOW()
      AND re.${situation} IS TRUE;
    `

    const { rows } = await client.query(query, [longitude, latitude])
    if (rows.length < 1) {
      const output: Output = {
        alertLevel: null,
        alertLevelValue: null,
        document: null,
        restrictions: null,
      }

      return {
        statusCode: 200,
        body: JSON.stringify(output),
      }
    }

    const restrictionsUniqueCollection = {}
    const alertNumberMapping = {
      vigilance: 1,
      alerte: 2,
      'alerte renforcée': 3,
      crise: 4,
    }

    for (const restriction of rows) {
      const restrictionIdentifier = `${restriction.theme}${restriction.label}`
      const cacheAlertLevelNumber =
        alertNumberMapping[restrictionsUniqueCollection[restrictionIdentifier]?.alertLevel] || 0
      const alertLevelNumber = alertNumberMapping[restriction.alertLevel]

      if (cacheAlertLevelNumber > alertLevelNumber) {
        continue
      }

      restrictionsUniqueCollection[restrictionIdentifier] = restriction
    }

    const restrictionValues: Array<any> = Object.values(restrictionsUniqueCollection)
    const restrictions = restrictionValues.map((restriction) => {
      restriction.slug = `${slugify(restriction.restrictionLevel)}-${slugify(restriction.theme)}`
      const { alertLevel, document, type, ...rest } = restriction

      return rest
    })

    const output: Output = {
      alertLevel: restrictionValues[0].alertLevel,
      alertLevelValue: alertNumberMapping[restrictionValues[0].alertLevel] ?? null,
      document: `https://propluvia-data.s3.gra.io.cloud.ovh.net/pdf/${restrictionValues[0].document}`,
      restrictions,
    }

    return {
      statusCode: 200,
      body: JSON.stringify(output),
    }
  } catch (error) {
    console.error(error)

    return {
      statusCode: 500,
      body: '',
    }
  } finally {
    !!client && (await client.end())
  }
}

const validateQuery = (queryParameters: QueryParameters): ErrorOutput | undefined => {
  const { latitude, longitude, situation } = queryParameters

  if (!latitude || !longitude || !situation) {
    const errors = {}

    if (!latitude) {
      errors['latitude'] = 'Missing value'
    }

    if (!longitude) {
      errors['longitude'] = 'Missing value'
    }

    if (!situation) {
      errors['situation'] = 'Missing value'
    }

    if ('individual' !== situation && 'company' !== situation && 'community' !== situation && 'farming' !== situation) {
      errors['situation'] = 'Value must be one of: `individual|company|community|farming`'
    }

    return {
      type: 'missing_queryparameters',
      title: 'One or more query parameters are missing',
      errors,
    }
  }
}

const slugify = (text: string) =>
  text
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')
