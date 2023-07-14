from datetime import datetime
from typing import Optional

class Geozone:
    def __init__(self, id: Optional[int], external_id: str, geometry):
        self.id = id
        self.external_id = external_id
        self.geometry = geometry
