import datetime

def find_by_external_id(cursor, external_id: str):
    query = 'SELECT id FROM decree WHERE external_id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)

    return cursor.fetchone()

def save(cursor, external_id: str, geozone_id: str, alert_level: str, start_date: datetime, end_date: datetime) -> None:
    query = 'INSERT INTO decree (external_id, geozone_id, alert_level, start_date, end_date) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (external_id) DO UPDATE SET geozone_id = EXCLUDED.geozone_id, alert_level = EXCLUDED.alert_level, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date;'
    parameters = (external_id, geozone_id, alert_level, start_date, end_date)
    cursor.execute(query, parameters)

    return
