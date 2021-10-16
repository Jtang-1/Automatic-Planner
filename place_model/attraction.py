from place_model.place import Place
default_visit_minutes = 400  # minutes


class Attraction(Place):
    def __init__(self, place_id: str, name: str, place_type: str = None,
                 opening_hours: dict = None, business_status: str = None, visit_minutes: int = default_visit_minutes):
        self.visit_minutes = visit_minutes
        super().__init__(place_id, name, place_type, opening_hours, business_status)
