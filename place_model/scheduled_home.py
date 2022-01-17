from place_model.home import Home


class ScheduledHome(Home):
    def __init__(self, home):
        self.base_place = home
        self.arrive_time = None
        self.leave_time = None
        super().__init__(place_id=home.place_id, name=home.name, lng=home.lng, lat=home.lat,
                         opening_hours=home.opening_hours, business_status=home.business_status)

    def set_arrive_time(self, arrive_time):
        self.arrive_time = arrive_time

    def set_leave_time(self, leave_time):
        self.leave_time = leave_time
