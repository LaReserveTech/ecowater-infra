def wipe(cursor) -> None:
    query = 'TRUNCATE restriction'
    cursor.execute(query)

    return

def save(cursor, decree_id: int, restriction_level: str, user_individual: bool, user_company: bool, user_community: bool, user_farming: bool, theme: str, label: str, description: str, specification: str, from_hour, to_hour) -> None:
    query = 'INSERT INTO restriction (decree_id, restriction_level, user_individual, user_company, user_community, user_farming, theme, label, description, specification, from_hour, to_hour) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    parameters = (decree_id, restriction_level, user_individual, user_company, user_community, user_farming, theme, label, description, specification, from_hour, to_hour)
    cursor.execute(query, parameters)

    return
