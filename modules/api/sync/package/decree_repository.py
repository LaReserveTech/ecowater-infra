from typing import Optional

from decree import Decree

def find_by_external_id(cursor, external_id: str) -> Optional[Decree]:
    query = 'SELECT * FROM decree WHERE external_id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)
    result = cursor.fetchone()

    if not result:
        return None

    return Decree(
        id = result.get('id'),
        external_id = result.get('external_id'),
        geozone_id = result.get('geozone_id'),
        alert_level = result.get('alert_level'),
        start_date = result.get('start_date'),
        end_date = result.get('end_date'),
        document = result.get('document'),
    )

def insert(cursor, decree: Decree) -> int:
    query = 'INSERT INTO decree (external_id, geozone_id, alert_level, start_date, end_date, document) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;'
    parameters = (decree.external_id, decree.geozone_id, decree.alert_level, decree.start_date, decree.end_date, decree.document)
    cursor.execute(query, parameters)

    return cursor.fetchone()[0]

def update(cursor, decree: Decree) -> None:
    query = 'UPDATE decree SET end_date = %s WHERE id = %s;'
    parameters = (decree.end_date, decree.id)
    cursor.execute(query, parameters)

    return
