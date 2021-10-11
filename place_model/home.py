from place_model.place import Place


class Home(Place):
    def __init__(self, place_id: str, name: str,
                 opening_hours: dict = None, business_status: str = None):
        self.place_type = "home"
        super().__init__(place_id, name, self.place_type, opening_hours, business_status)
