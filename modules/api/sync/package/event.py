from enum import Enum

class Event(Enum):
    GEOZONE_CREATION = 'geozone_creation'
    DECREE_CREATION = 'decree_creation'
    DECREE_REPEAL = 'decree_repeal'
