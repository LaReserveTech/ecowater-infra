from typing import Optional

class Geozone:
    def __init__(self, id: Optional[int], external_id: str, type: str, name: str, geometry):
        self.id = id
        self.external_id = external_id
        self.type = type
        self.name = name
        self.geometry = geometry
