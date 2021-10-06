import json
import jsonpickle


class Place():
    def __init__(self, place_id: str, name: str,
                 place_type: str = None, opening_hours: dict = None, business_status: str = None):
        self.place_id = place_id
        self.name = name
        self.place_type = place_type
        self.opening_hours = opening_hours
        self.business_status = business_status

    def to_json(self):
        return jsonpickle.encode(self)

    def get_name(self):
        return self.name
