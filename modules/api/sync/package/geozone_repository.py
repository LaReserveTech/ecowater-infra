def find_by_external_id(cursor, external_id: str):
    query = 'SELECT id FROM geozone WHERE id_zone = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)

    return cursor.fetchone()
