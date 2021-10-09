from place_model.place import Place


class Home(Place):
    def __init__(self, place_id: str, name: str,
                 place_type: "home", opening_hours: dict = None, business_status: str = None):
        super().__init__(place_id, name, place_type, opening_hours, business_status)
