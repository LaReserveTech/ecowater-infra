from typing import List,  Optional
from models import Decree, Event


def find_all_decree_events(cursor) -> List[Event]:
    cursor.execute("SELECT * FROM event_store WHERE type IN ('decree_creation', 'decree_repeal');")
    results = cursor.fetchall()
    return [] if not results else results

def delete_event(cursor, event_id: int):
    query = 'DELETE FROM event_store WHERE id = %s'
    parameters = (event_id,)
    cursor.execute(query, parameters)
