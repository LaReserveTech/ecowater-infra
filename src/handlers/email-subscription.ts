import 'dotenv/config'
import { Handler } from 'aws-lambda'
import { Client } from 'pg'

const validateEmail = (email: string) => {
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    )
}

type subscribeEmailEvent = {
  queryStringParameters: {
    address?: string
    latitude?: number
    longitude?: number
    email?: string
  }
}

const subscribeEmail: Handler = async (event: subscribeEmailEvent) => {
  const {
    queryStringParameters: { latitude, longitude, email, address },
  } = event

  if (!latitude || !longitude || !email || !address) {
    return {
      statusCode: '400',
      body: "A parameter is missing. Parameters should be 'longitude', 'latitude', 'email' and 'address'.",
    }
  }

  if (!validateEmail(email)) {
    return {
      statusCode: '400',
      body: 'Email is not valid',
    }
  }

  const client = new Client()
  await client.connect()
  console.log('Connected to the database')

  try {
    const checkQuery = `SELECT email FROM alert_subscription WHERE email = $1;`
    const { rows } = await client.query(checkQuery, [email])
    if (rows.length > 0) {
      return {
        statusCode: '400',
        body: 'This email adress is already used in our database',
      }
    }

    const query = `INSERT into alert_subscription (email, address, longitude, latitude, subscribed_at) VALUES ($1, $2, $3, $4, $5);`
    await client.query(query, [email, address, longitude, latitude, new Date()])
    return {
      statusCode: '204',
      body: '',
    }
  } catch (error) {
    console.error(error)
    return {
      statusCode: '500',
      body: '',
    }
  } finally {
    await client.end()
    console.log('Closed connection to the database')
  }
}

export default subscribeEmail
