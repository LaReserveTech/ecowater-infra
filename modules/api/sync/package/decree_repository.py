import datetime

def find_by_external_id(external_id: str):
    return {'geozone_id': 1, 'alert_level': 'vigilance'}

def save(cursor, external_id: str, geozone_external_id: str, alert_level: str, start_date: datetime, end_date: datetime) -> None:
    query = 'INSERT INTO decree (external_id, geozone_external_id, alert_level, start_date, end_date) VALUES (%s, %s, %s, %s, %s)'
    parameters = (external_id, geozone_external_id, alert_level, start_date, end_date)
    cursor.execute(query, parameters)

    return
