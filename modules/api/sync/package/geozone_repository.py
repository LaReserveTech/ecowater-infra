def find_by_external_id(cursor, external_id: str):
    query = 'SELECT gid FROM geozone WHERE id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)

    return cursor.fetchone()
