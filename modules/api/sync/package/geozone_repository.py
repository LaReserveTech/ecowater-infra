from typing import Optional

from geozone import Geozone

def find_by_external_id(cursor, external_id: str) -> Optional[Geozone]:
    query = 'SELECT id, external_id, geometry FROM geozone WHERE external_id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)
    result = cursor.fetchone()

    if not result:
        return None

    return Geozone(
        id = result.get('id'),
        type = result.get('type'),
        name = result.get('name'),
        external_id = result.get('external_id'),
        geometry = result.get('geometry'),
    )

def insert(cursor, geozone: Geozone) -> int:
    query = 'INSERT INTO geozone (external_id, type, name, geometry) VALUES (%s, %s, %s, %s) RETURNING id;'
    parameters = (geozone.external_id, geozone.type, geozone.name, geozone.geometry)
    cursor.execute(query, parameters)

    return cursor.fetchone()[0]
