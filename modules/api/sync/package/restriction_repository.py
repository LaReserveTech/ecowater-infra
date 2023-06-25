from restriction import Restriction

def save(cursor, restriction: Restriction) -> None:
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
        restriction.external_id,
        restriction.decree_id,
        restriction.restriction_level,
        restriction.user_individual,
        restriction.user_company,
        restriction.user_community,
        restriction.user_farming,
        restriction.theme,
        restriction.label,
        restriction.description,
        restriction.specification,
        restriction.from_hour,
        restriction.to_hour,
    )
    cursor.execute(query, parameters)

    return
