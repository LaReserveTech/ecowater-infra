from typing import List,  Optional
from models import Decree, Event


def find_all_events(cursor) -> List[Event]:
    cursor.execute('SELECT * FROM event_store;')
    results = cursor.fetchall()

    return None if not results else results

def get_decree_by_id(cursor, id: str) -> Optional[Decree]:
    query = 'SELECT * FROM decree WHERE id = %s'
    parameters = (id,)
    cursor.execute(query, parameters)

    result = cursor.fetchone()
    if not result:
        return None

    return Decree(
        id=result.get('id'),
        external_id=result.get('external_id'),
        geozone_id=result.get('geozone_id'),
        alert_level=result.get('alert_level'),
        start_date=result.get('start_date'),
        end_date=result.get('end_date'),
        document=result.get('document')
    )


def get_user_emails_by_geozone_id(cursor, geozone_id: str) -> List[str]:
    query = """
        WITH geozone_geometry AS (
            SELECT geom as geometry
            FROM geozone
            WHERE id= %s
        )
        SELECT DISTINCT email
        FROM alert_subscription as user_details
        CROSS JOIN geozone_geometry
        WHERE ST_Contains(
            geozone_geometry.geometry,
            ST_SetSRID(
                ST_MakePoint(user_details.longitude, user_details.latitude),
                4326
            )
        );
    """
    params = (geozone_id,)
    cursor.execute(query, params)
    emails = cursor.fetchall()
    return emails