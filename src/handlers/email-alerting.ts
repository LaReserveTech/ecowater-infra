import 'dotenv/config'
import { Handler } from 'aws-lambda'
import { Client } from 'pg'
import { Mail, createEmail } from '../utils/create-email'
// need to keep the require here, the common syntax with import doesn't work
// see https://github.com/mailjet/mailjet-apiv3-nodejs/issues/217
const Mailjet = require('node-mailjet')

type Notification = {
  decreeId: number
  eventType: 'decree_repeal' | 'decree_creation'
}

type MailType = 'decree_repeal' | 'decree_creation' | 'decree_update'

const getEmailType = (notifications: Notification[]): MailType => {
  if (notifications.length === 1) return notifications[0].eventType
  const firstNotificationType = notifications[0].eventType
  const notificationsHaveDifferentType = notifications.some(
    (notification) => notification.eventType !== firstNotificationType
  )
  return notificationsHaveDifferentType ? 'decree_update' : firstNotificationType
}

const emailAlert: Handler = async () => {
  const client = new Client()
  await client.connect()
  console.log('Connected to the database')
  const mailjet = Mailjet.apiConnect(process.env.MJ_APIKEY_PUBLIC, process.env.MJ_APIKEY_PRIVATE)

  let success = false
  let userEmails: Record<string, Notification[]> = {}
  try {
    const { rows: events } = await client.query('SELECT * FROM event_store WHERE users_notified IS NOT true;')

    for await (const event of events) {
      try {
        const { rows: decrees } = await client.query('SELECT * FROM decree WHERE id = $1;', [event.stream_id])
        if (!decrees.length) {
          console.warn(`No decree was found for event ${event['id']}`)
          continue
        }
        const decree = decrees[0]
        const { rows: decreeUserEmails } = await client.query(
          `SELECT DISTINCT email
            FROM alert_subscription
            CROSS JOIN geozone
            WHERE geozone.id = $1
            AND ST_Contains(
              geozone.geometry,
              ST_SetSRID(
                ST_MakePoint(alert_subscription.longitude, alert_subscription.latitude),
                4326
              )
            );`,
          [decree.geozone_id]
        )

        if (decreeUserEmails.length) {
          decreeUserEmails.forEach((userEmail: { email: string }) => {
            const { email } = userEmail
            const newEmailContent = { decreeId: decree.id, eventType: event.type }
            if (Object.keys(userEmails).includes(email)) {
              userEmails = {
                ...userEmails,
                [email]: [...userEmails[email], newEmailContent],
              }
            } else {
              userEmails = {
                ...userEmails,
                [email]: [newEmailContent],
              }
            }
          })
        }

        await client.query('UPDATE event_store SET users_notified = true WHERE id = $1;', [event.id])
      } catch (e) {
        console.error(e)
        console.error(`couldn't get emails for decree ${event.stream_id}`)
      }
    }
  } catch (error) {
    console.error(error)
  } finally {
    await client.end()
    console.log('Closed connection to the database')
  }

  const mails = Object.keys(userEmails).reduce((result, userEmail) => {
    const notifications = userEmails[userEmail]
    if (!notifications.length) return result
    const mailType = getEmailType(notifications)
    return [
      ...result,
      {
        mail: createEmail(userEmail),
        mailType,
        emailAddress: userEmail,
      },
    ]
  }, [] as { mail: Mail; mailType: MailType; emailAddress: string }[])

  for await (const email of mails) {
    try {
      console.log('on envoie les mails', mails)
      // await mailjet
      //   .post('send', { version: 'v3.1' })
      //   .request({
      //     Messages: email.mail,
      //   })
      //   .catch((err) => {
      //     console.log(err.statusCode)
      //   })
    } catch (e) {
      console.error(e)
      console.error(`couldn't send emails to ${email.emailAddress}`)
    }
  }

  success = true

  return success
    ? {
        statusCode: '200',
        body: 'Users successfully alerted',
      }
    : {
        statusCode: '500',
        body: 'Something failed',
      }
}

export default emailAlert
