from typing import Optional

class Restriction:
    def __init__(self, id: Optional[int], decree_id: int, restriction_level: str, user_individual: bool, user_company: bool, user_community: bool, user_farming: bool, theme: str, label: str, description: str, specification: str, from_hour: int, to_hour: int):
        self.id = id
        external_id = external_id
        decree_id = decree_id
        restriction_level = restriction_level
        user_individual = user_individual
        user_company = user_company
        user_community = user_community
        user_farming = user_farming
        theme = theme
        label = label
        description = description
        specification = specification
        from_hour = from_hour
        to_hour = to_hour
