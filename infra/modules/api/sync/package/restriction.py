from typing import Optional

class Restriction:
    def __init__(self, id: Optional[int], external_id: str, decree_id: int, restriction_level: str, user_individual: bool, user_company: bool, user_community: bool, user_farming: bool, theme: str, label: str, description: str, specification: str, from_hour: int, to_hour: int):
        self.id = id
        self.external_id = external_id
        self.decree_id = decree_id
        self.restriction_level = restriction_level
        self.user_individual = user_individual
        self.user_company = user_company
        self.user_community = user_community
        self.user_farming = user_farming
        self.theme = theme
        self.label = label
        self.description = description
        self.specification = specification
        self.from_hour = from_hour
        self.to_hour = to_hour
