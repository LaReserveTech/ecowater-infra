from typing import List

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
