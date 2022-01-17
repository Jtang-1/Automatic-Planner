from place_model.attraction import Attraction
default_visit_minutes = 900  # minutes


class ScheduledAttraction(Attraction):
    def __init__(self, attraction, arrive_time, leave_time):
        self.base_place = attraction
        self.arrive_time = arrive_time
        self.leave_time = leave_time
        super().__init__(place_id=attraction.place_id, name=attraction.name, lng=attraction.lng,
                         lat=attraction.lat, place_type=attraction.place_type, opening_hours=attraction.opening_hours,
                         business_status=attraction.business_status, visit_minutes=attraction.visit_minutes)
