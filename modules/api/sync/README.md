# Sync

## Getting Started

```console
docker compose up -d
docker compose run --rm ogr2ogr ogr2ogr -f "PostgreSQL" PG:"host=pg port=5432 dbname=ecowater user=ecowater password=ecowater" "/app/all_zones.shp" -nln geozone -nlt PROMOTE_TO_MULTI -s_srs "/app/all_zones.prj" -t_srs "EPSG:4326" -lco FID=id -lco GEOMETRY_NAME=geom -progress
docker compose run --rm app pip install -r requirements.txt
docker compose run --rm app python index.py
```
