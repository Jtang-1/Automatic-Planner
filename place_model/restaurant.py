from place_model.place import Place


class Restaurant(Place):
    def __init__(self, place_id: str, name: str,
                 place_type: "origin", opening_hours: dict = None, business_status: str = None):
        super().__init__(place_id, name, place_type, opening_hours, business_status)
