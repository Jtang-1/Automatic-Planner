import datetime

# NEED TO STORE OPEN TIME/ CLOSE TIMES AS DICTIONARY CONTAINING LIST AS VALUE. WHEN CHECKING is_open_start_of_visit
# IN SHORTEST PATH, NEED TO CHECK IF BETWEEN OPEN AND CLOSE TIME
# IN GENERAL, WHEN READING INFO, USE open_close times = zip(OPEN_TIMES["day"], CLOSE_TIMES["day"]). For time in
# For open_time, close_time in open_close_times...
def create_open_close_times(opening_hours, state: str = "open") -> {int, datetime.time}:
    state_times = {}
    if opening_hours is None or is_always_open(opening_hours["periods"][0]):
        if state == "open":
            return dict.fromkeys([0, 1, 2, 3, 4, 5, 6], datetime.time(0, 0))
        if state == "close":
            return dict.fromkeys([0, 1, 2, 3, 4, 5, 6], datetime.time(23, 59, 59))
    day_of_week_count = 0
    for period in opening_hours["periods"]:
        while day_of_week_count < period["open"]["day"]:
            # None signifies closed for day
            state_time = None
            state_times[day_of_week_count] = state_time
            day_of_week_count += 1
        open_day = period["open"]["day"]
        close_day = period["close"]["day"]
        if state == "close" and close_day >= (open_day+1) % 7:
            state_time = datetime.time(23, 59)
        else:
            state_time_hour = period[state]["hours"]
            state_time_minute = period[state]["minutes"]
            state_time = datetime.time(state_time_hour, state_time_minute)
        state_times[open_day] = state_time
        day_of_week_count += 1
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
    def __init__(self, place_id: str, name: str,
                 place_type: str = None, opening_hours: dict = None, business_status: str = None):
        self.place_id = place_id
        self.name = name
        self.place_type = place_type
        self.opening_hours = opening_hours
        self.business_status = business_status
        self.open_times = create_open_times(opening_hours)
        self.close_times = create_close_times(opening_hours)

    def is_closed_on(self, weekday: int):
        if self.open_times[weekday] is None:
            return True
        return False

