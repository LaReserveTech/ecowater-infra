import 'dotenv/config'
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda'
import { Client } from 'pg'

interface QueryParameters {
  latitude?: string,
  longitude?: string,
  situation?: string,
}

interface ErrorOutput {
  type: string,
  title: string,
  errors: Error,
}

interface Error {
  [error: string]: string,
}

export default async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  let client: Client|undefined

  try {
    client = new Client()
    await client.connect()

    const query = `
      SELECT COUNT(alert_level) AS "alertLevelNumber", alert_level AS "alertLevel"
      FROM decree
      WHERE start_date <= NOW()
        AND end_date >= NOW()
      GROUP BY alert_level;
    `
    type QueryResult = { rows: { alertLevelNumber: string, alertLevel: string }[] }
    const { rows }: QueryResult = await client.query(query)

    const alertNumbersOutput: { [alertLevel: string]: number|null } = {}
    const alertNumbers = rows.reduce((acc, { alertLevelNumber, alertLevel }) => (
      { ...acc, [alertLevel]: parseInt(alertLevelNumber) || null }
    ), alertNumbersOutput)

    return {
      statusCode: 200,
      body: JSON.stringify(alertNumbers),
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
