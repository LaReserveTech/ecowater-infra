import datetime

def find_by_external_id(cursor, external_id: str):
    query = 'SELECT id FROM decree WHERE external_id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)

    return cursor.fetchone()

def save(cursor, decree) -> None:
    query = 'INSERT INTO decree (external_id, geozone_id, alert_level, start_date, end_date) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (external_id) DO UPDATE SET geozone_id = EXCLUDED.geozone_id, alert_level = EXCLUDED.alert_level, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date;'
    parameters = (decree.get('external_id'), decree.get('geozone_id'), decree.get('alert_level'), decree.get('start_date'), decree.get('end_date'))
    cursor.execute(query, parameters)

    return
