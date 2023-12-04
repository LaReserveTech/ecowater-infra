import 'dotenv/config'
import { Handler } from 'aws-lambda'
import { Client } from 'pg'
import { fetchDecrees } from '../utils/decree-provider'

type Event = {
  decreeId: number
  type: 'decree_repeal' | 'decree_creation'
}

const synchronize: Handler = async (_event: any) => {
  console.log('Decrees synchronization started')
  const client = new Client()
  await client.connect()
  console.log('Connected to the database')

  const eventsToDispatch: Event[] = []

  const report = {
    creations: 0,
    repeals: 0,
    missingGeozone: 0,
  }

  try {
    console.log('Fetching decrees')
    const decrees = await fetchDecrees()
    console.log('Fetched decrees')
    console.log('Synchronizing...')

    for (const decree of decrees) {
      // manage existing decree
      const existingDecrees = await client.query('SELECT id, end_date, repealed FROM decree WHERE external_id = $1', [
        decree['unique_key_arrete_zone_alerte'],
      ])
      if (existingDecrees.rows.length > 0) {
        const existingDecree = existingDecrees.rows[0]
        if (!existingDecree.repealed) {
          if (decree['statut_arrete'] === 'Terminé') {
            await client.query('UPDATE decree SET end_date = $1, repealed = TRUE WHERE external_id = $2', [
              decree['fin_validite_arrete'],
              decree['unique_key_arrete_zone_alerte'],
            ])
            eventsToDispatch.push({ decreeId: existingDecree.id, type: 'decree_repeal' })
            report.repeals = report.repeals + 1
          }
        }
        continue
      }

      // manage repealed decree but not present in the database
      if (decree['statut_arrete'] === 'Terminé') {
        continue
      }

      // manage new decree
      const res = await client.query('SELECT id FROM geozone WHERE external_id = $1', [decree['id_zone']])

      const geozoneId = res?.rows[0]?.id
      if (!geozoneId) {
        console.warn(
          `Decree cannot be synchronized, missing geozone. Geozone ID: ${decree['id_zone']}, External ID: ${decree['unique_key_arrete_zone_alerte']}`
        )
        report.missingGeozone = report.missingGeozone + 1
        continue
      }

      const query = `
        INSERT INTO decree (external_id, geozone_id, alert_level, start_date, end_date, document)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (external_id) DO UPDATE
        SET geozone_id = EXCLUDED.geozone_id, alert_level = EXCLUDED.alert_level, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, document = EXCLUDED.document
        RETURNING id;
      `

      const { rows: decrees } = await client.query(query, [
        decree['unique_key_arrete_zone_alerte'],
        geozoneId,
        decree['nom_niveau'].toLowerCase(),
        decree['debut_validite_arrete'],
        decree['fin_validite_arrete'] || null,
        decree['chemin_fichier'],
      ])

      if (!decrees.length) {
        console.warn(
          `Decree was not created. Geozone ID: ${decree['id_zone']}, External ID: ${decree['unique_key_arrete_zone_alerte']}`
        )
        continue
      }

      report.creations = report.creations + 1
      eventsToDispatch.push({ decreeId: decrees[0].id, type: 'decree_creation' })
    }

    const eventCreationQuery = `
        INSERT INTO event_store (stream_id, type, payload, occurred_at) VALUES ($1, $2, NULL, $3);
      `
    for (const event of eventsToDispatch) {
      // later manage case where a decree is closed and a new one is created at the same time
      await client.query(eventCreationQuery, [event.decreeId, event.type, new Date()])
    }

    console.log('Decrees synchronization successfull')
  } catch (error) {
    console.error(error)
  } finally {
    await client.end()
    console.log('Closed connection to the database')
  }

  console.log(report)
}

export default synchronize
