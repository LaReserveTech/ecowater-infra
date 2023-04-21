import datetime

def update_alert_level(cursor, external_id: str, alert_level: str) -> None:
    query = 'UPDATE geozone SET alert_level = %s WHERE external_id = %s'
    parameters = (external_id, alert_level)
    cursor.execute(query, parameters)

    return
