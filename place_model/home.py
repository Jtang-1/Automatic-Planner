from place_model.place import Place


class Home(Place):
    def __init__(self, place_id: str, name: str, lng: float, lat: float,
                 opening_hours: dict = None, business_status: str = None):
        self.place_type = "home"
        self.visit_minutes = None
        super().__init__(place_id=place_id, name=name, lat=lat, lng=lng, place_type=self.place_type,
                         opening_hours=None, business_status=business_status)
