from datetime import datetime
from typing import Optional

class Decree:
    def __init__(self, id: Optional[int], external_id: str, geozone_id: int, alert_level: str, start_date: datetime, end_date: datetime, document: str):
        self.id = id
        self.external_id = external_id
        self.geozone_id = geozone_id
        self.alert_level = alert_level
        self.start_date = start_date
        self.end_date = end_date
        self.document = document

    def repeal(self, repeal_date) -> 'Decree':
        self.end_date = repeal_date

        return self
