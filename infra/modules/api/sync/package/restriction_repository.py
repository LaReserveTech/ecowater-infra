from typing import Optional

from restriction import Restriction

def find_by_external_id(cursor, external_id: str) -> Optional[Restriction]:
    query = 'SELECT * FROM restriction WHERE external_id = %s'
    parameters = (external_id,)
    cursor.execute(query, parameters)
    result = cursor.fetchone()

    if not result:
        return None

    return Restriction(
        id = result.get('id'),
        external_id = result.get('external_id'),
        decree_id = result.get('decree_id'),
        restriction_level = result.get('restriction_level'),
        user_individual = result.get('user_individual'),
        user_company = result.get('user_company'),
        user_community = result.get('user_community'),
        user_farming = result.get('user_farming'),
        theme = result.get('theme'),
        label = result.get('label'),
        description = result.get('description'),
        specification = result.get('specification'),
        from_hour = result.get('from_hour'),
        to_hour = result.get('to_hour'),
    )

def insert(cursor, restriction: Restriction) -> None:
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
        RETURNING id
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

    return cursor.fetchone()[0]

def update(cursor, restriction: Restriction) -> None:
    query = """
        UPDATE restriction SET
            external_id = %s,
            decree_id = %s,
            restriction_level = %s,
            user_individual = %s,
            user_company = %s,
            user_community = %s,
            user_farming = %s,
            theme = %s,
            label = %s,
            description = %s,
            specification = %s,
            from_hour = %s,
            to_hour = %s
        WHERE id = %s;
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
        restriction.id,
    )
    cursor.execute(query, parameters)

    return
