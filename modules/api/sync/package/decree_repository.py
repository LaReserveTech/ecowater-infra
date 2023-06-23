from datetime import datetime, timedelta

def find_by_external_id(cursor, external_id: str):
    query = 'SELECT id, end_date FROM decree WHERE external_id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)

    return cursor.fetchone()

def save(cursor, decree) -> None:
    query = 'INSERT INTO decree (external_id, geozone_id, alert_level, start_date, end_date, document) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (external_id) DO UPDATE SET geozone_id = EXCLUDED.geozone_id, alert_level = EXCLUDED.alert_level, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, document = EXCLUDED.document;'
    parameters = (decree.get('external_id'), decree.get('geozone_id'), decree.get('alert_level'), decree.get('start_date'), decree.get('end_date'), decree.get('document'))
    cursor.execute(query, parameters)
    return

def update(cursor, external_id, end_date) -> None:
    query = 'UPDATE decree SET end_date = %s, updated_at=%s WHERE external_id = %s;'
    current_date = datetime.today() + timedelta(days=1)
    parameters = (end_date, current_date, external_id)
    cursor.execute(query, parameters)
    return
