import datetime

def save(cursor, decree_id, restriction) -> None:
    query = 'INSERT INTO restriction (dec, geozone_external_id, alert_level, start_date, end_date) VALUES (%s, %s, %s, %s, %s)'
    parameters = (external_id, geozone_external_id, alert_level, start_date, end_date)
    cursor.execute(query, parameters)

    return
