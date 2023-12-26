# EcoWater's Source Code

## Get Started

Prerequisites:

- Node & Npm
- Docker & Docker Compose
- Serverless

```bash
<node-version-manager> use
npm install
docker compose up -d
```

## Serverless

```bash
serverless invoke local --function synchronize-geozones
serverless invoke local --function synchronize-decrees
serverless invoke local --function synchronize-restrictions
serverless invoke local --function email-alerting
serverless invoke local --function restrictions-query -p events/restriction-query.json
serverless invoke local --function alert-numbers-query -p events/alert-numbers-query.json
```

Subscribe a new email (example data: Baixas 66390)

```bash
serverless invoke local --function email-subscription  --path events/email-subscription.json
```

```bash
serverless deploy --stage staging
serverless deploy --stage prod
```

## SQL Commands

Get center point long lat of the first geozone:

```sql
SELECT gz.id, gz.name, ST_X(ST_Centroid(gz.geometry)) as longitude, ST_Y(ST_Centroid(gz.geometry)) as latitude, de.alert_level, re.user_individual
FROM geozone AS gz
INNER JOIN decree AS de ON de.geozone_id = gz.id
INNER JOIN restriction AS re ON re.decree_id = de.id
WHERE de.start_date <= NOW() AND de.end_date >= NOW()
LIMIT 1;
```

Find geozones by lat long:

```sql
SELECT gz.id, gz.external_id, gz.type, gz.name, de.alert_level
FROM geozone AS gz
INNER JOIN decree AS de ON de.geozone_id = gz.id
WHERE ST_Contains(
    gz.geometry,
    ST_SetSRID(
        ST_MakePoint(1.5981400261970788, 49.86838403638272),
        4326
    )
);
```
