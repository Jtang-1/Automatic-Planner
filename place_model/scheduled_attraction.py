from place_model.attraction import Attraction
default_visit_minutes = 900  # minutes


class ScheduledAttraction(Attraction):
    def __init__(self, attraction, arrive_time, leave_time):
        self.base_place = attraction
        self.arrive_time = arrive_time
        self.leave_time = leave_time
        super().__init__(attraction.place_id, attraction.name, attraction.place_type, attraction.opening_hours,
                         attraction.business_status, attraction.visit_minutes)

