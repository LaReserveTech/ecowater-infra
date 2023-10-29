# EcoWater's Source Code

## Get Started

Prerequisites:
- Node & Npm
- Docker & Docker Compose

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
```

```bash
serverless deploy --stage staging
serverless deploy --stage prod
```

## SQL Commands

Get center point long lat of the first geozone:
```sql
SELECT id, name, ST_X(ST_Centroid(geometry)) as longitude, ST_Y(ST_Centroid(geometry)) as latitude
FROM geozone gz
LIMIT 1;
```

Find geozones by lat long:
```sql
SELECT gz.id, gz.external_id, gz.type, gz.name
FROM geozone gz
WHERE ST_Contains(
    gz.geometry,
    ST_SetSRID(
        ST_MakePoint(4.356850234425376, 49.4610139711892),
        4326
    )
);
```
