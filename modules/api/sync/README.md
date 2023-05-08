# Sync

## Getting Started

```
docker compose up -d
docker compose run --rm app pip install -r requirements.txt
docker compose run --rm app python index.py
```

```
docker run --rm -it --volume `pwd`:/app --workdir /app jjrom/shp2pgsql -I -s 4326 -g geom zonesalerte.shp geozone > zonesalerte.sql
```