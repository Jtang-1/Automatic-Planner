import datetime


def create_open_close_times(opening_hours, state: str = "open") -> {int: [datetime.time]}:
    state_times = {}
    if opening_hours is None or is_always_open(opening_hours["periods"][0]):
        if state == "open":
            return dict.fromkeys([0, 1, 2, 3, 4, 5, 6], [datetime.time(0, 0)])
        if state == "close":
            return dict.fromkeys([0, 1, 2, 3, 4, 5, 6], [datetime.time(23, 59, 59)])
    day_of_week_count = 0
    for period in opening_hours["periods"]:
        open_day = period["open"]["day"]
        while day_of_week_count < open_day:
            # None signifies closed for day
            state_times[day_of_week_count] = None
            day_of_week_count += 1
        if day_of_week_count not in state_times and day_of_week_count < 7:
            state_times[day_of_week_count] = []
        close_day = period["close"]["day"]
        if state == "close" and close_day == (open_day+1) % 7:
            state_time = datetime.time(23, 59)
        else:
            state_time_hour = period[state]["hours"]
            state_time_minute = period[state]["minutes"]
            state_time = datetime.time(state_time_hour, state_time_minute)
        day_of_week_count = open_day + 1
        state_times[open_day].append(state_time)
    print("final statetime is", state_times)

    return state_times


def create_open_times(opening_hours) -> {int, datetime.time}:
    return create_open_close_times(opening_hours, "open")


def create_close_times(opening_hours) -> {int, datetime.time}:
    return create_open_close_times(opening_hours, "close")


def is_always_open(periods) -> bool:
    if "close" not in periods:
        return True
    return False

class Place:
    def __init__(self, place_id: str, name: str, lng: float, lat: float, place_type: str = None,
                 opening_hours: dict = None, business_status: str = None):
        self.place_id = place_id
        self.name = name
        self.place_type = place_type
        self.opening_hours = opening_hours
        self.business_status = business_status
        self.open_times = create_open_times(opening_hours)
        self.close_times = create_close_times(opening_hours)
        self.lng = lng
        self.lat = lat

    def is_closed_on(self, weekday: int):
        if self.open_times[weekday] is None:
            return True
        return False

