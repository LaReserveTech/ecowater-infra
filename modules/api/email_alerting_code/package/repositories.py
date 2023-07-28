from typing import List,  Optional
from models import Decree, Event


def find_all_decree_events(cursor) -> List[Event]:
    cursor.execute("SELECT * FROM event_store WHERE type IN ('decree_creation', 'decree_repeal');")
    results = cursor.fetchall()
    return [] if not results else results

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


def find_user_emails_by_geozone_id(cursor, geozone_id: str) -> List[str]:
    query = """
        SELECT DISTINCT email
        FROM alert_subscription
        CROSS JOIN geozone
        WHERE geozone.id = %s
        AND ST_Contains(
	        geozone.geom,
	        ST_SetSRID(
		        ST_MakePoint(alert_subscription.longitude, alert_subscription.latitude),
		        4326
	        )
        );
    """
    params = (geozone_id,)
    cursor.execute(query, params)
    emails = cursor.fetchall()
    return emails

def delete_event(cursor, event_id: int):
    query = 'DELETE FROM event_store WHERE id = %s'
    parameters = (event_id,)
    cursor.execute(query, parameters)
