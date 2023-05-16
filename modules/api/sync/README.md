# Sync

## Getting Started

```console
docker compose up -d
docker compose run --rm ogr2ogr ogr2ogr -f "PostgreSQL" PG:"host=pg port=5432 dbname=ecowater user=ecowater password=ecowater" "/app/sql_statement.shp" -nln geozone -nlt PROMOTE_TO_MULTI -s_srs "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +datum=WGS84 +units=m +no_defs" -t_srs "EPSG:4326" -lco FID=id -lco GEOMETRY_NAME=geom -progress
docker compose run --rm app pip install -r requirements.txt
docker compose run --rm app python index.py
```
