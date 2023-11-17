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
    latitude?: number
    longitude?: number
    email?: string
  }
}

const subscribeEmail: Handler = async (event: subscribeEmailEvent) => {
  const {
    queryStringParameters: { latitude, longitude, email },
  } = event

  if (!latitude || !longitude || !email) {
    return {
      statusCode: '400',
      body: "A parameter is missing. Parameters should be 'longitude', 'latitude', and 'email'",
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
    const query = `INSERT into alert_subscription (email, longitude, latitude, subscribed_at) VALUES ($1, $2, $3, $4);`
    await client.query(query, [email, longitude, latitude, new Date()])
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
