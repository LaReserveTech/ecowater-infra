import json
from typing import Optional
from datetime import datetime

from event import Event

class EventDispatcher:
    def __init__(self, cursor):
        self.cursor = cursor

    def dispatch(self, event: Event, streamId: int, payload: Optional[dict]):
        query = 'INSERT INTO event_store (stream_id, type, payload, occurred_at) VALUES (%s, %s, %s, %s);'
        parameters = (streamId, event.value, payload, datetime.now())
        self.cursor.execute(query, parameters)

        return
