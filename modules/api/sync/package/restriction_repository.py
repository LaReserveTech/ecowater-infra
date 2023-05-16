def wipe(cursor) -> None:
    query = 'TRUNCATE restriction'
    cursor.execute(query)

    return

def save(cursor, restriction) -> None:
    query = """
        INSERT INTO restriction (
            external_id,
            decree_id,
            restriction_level,
            user_individual,
            user_company,
            user_community,
            user_farming,
            theme,
            label,
            description,
            specification,
            from_hour,
            to_hour
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(external_id)
        DO UPDATE SET
            decree_id = EXCLUDED.decree_id,
            restriction_level = EXCLUDED.restriction_level,
            user_individual = EXCLUDED.user_individual,
            user_company = EXCLUDED.user_company,
            user_community = EXCLUDED.user_community,
            user_farming = EXCLUDED.user_farming,
            theme = EXCLUDED.theme,
            label = EXCLUDED.label,
            description = EXCLUDED.description,
            specification = EXCLUDED.specification,
            from_hour = EXCLUDED.from_hour,
            to_hour = EXCLUDED.to_hour
        ;
    """
    parameters = (
        restriction.get('external_id'),
        restriction.get('decree_id'),
        restriction.get('restriction_level'),
        restriction.get('user_individual'),
        restriction.get('user_company'),
        restriction.get('user_community'),
        restriction.get('user_farming'),
        restriction.get('theme'),
        restriction.get('label'),
        restriction.get('description'),
        restriction.get('specification'),
        restriction.get('from_hour'),
        restriction.get('to_hour'),
    )
    cursor.execute(query,
    parameters)

    return
