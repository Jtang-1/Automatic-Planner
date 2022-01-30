from place_model.place import Place
from place_model.attraction import Attraction
from place_model.scheduled_attraction import ScheduledAttraction
from place_model.scheduled_home import ScheduledHome
from place_model.home import Home
from place_model.edge import Edge
import datetime
from place_model.place_graph import PlaceGraph
import datetime



class DayItinerary:
    def __init__(self, start_date_time: datetime.datetime, end_date_time: datetime.datetime,
                 is_driving_allowed: bool = True, locations: [Place] = None):
        self.is_driving_allowed = is_driving_allowed
        self.scheduled_home = None
        self.scheduled_locations = []
        self.transport: [Edge] = []
        self.start_date_time = start_date_time
        self.current_date_time = start_date_time
        self.end_date_time = end_date_time
        self.day_minutes = int((end_date_time - start_date_time).total_seconds() / 60)
        if locations:
            for location in locations:
                self.scheduled_locations.append(location)

    def add_home(self, location: Home):
        if not self.scheduled_home:
            self.scheduled_home = ScheduledHome(location)
        self.scheduled_locations.append(self.scheduled_home)

    def add_attraction(self, location: Attraction, arrive_time: datetime.time, leave_time: datetime.time):
        if isinstance(location, (list, set, tuple)):
            for loc in location:
                self.scheduled_locations.append(ScheduledAttraction(loc, arrive_time, leave_time))
        else:
            self.scheduled_locations.append(ScheduledAttraction(location, arrive_time, leave_time))

    def add_minutes_spent(self, minutes):
        minutes_spent = datetime.timedelta(minutes=minutes)
        self.current_date_time += minutes_spent

    @property
    def minutes_spent(self):
        return (self.current_date_time - self.start_date_time).total_seconds() / 60

    @property
    def date(self):
        return self.current_date_time.date()

    @property
    def current_time(self):
        return self.current_date_time.time()

    # 0 is Sunday per Google Place API
    @property
    def day_of_week(self):
        return (self.current_date_time.weekday() + 1) % 7

    @property
    def home(self):
        return self.scheduled_home.base_place

    def is_empty(self):
        if len(self.scheduled_locations):
            return False
        return True

    def add_edge(self, transport: Edge):
        self.transport.append(transport)

    def transport_info_from(self, scheduled_origin: Place) -> (int, str):
        # print("self.transport is", self.transport)
        for count, scheduled_location in enumerate(self.scheduled_locations):
            is_last_location = (count == (len(self.scheduled_locations) - 1))
            if scheduled_location == scheduled_origin and not is_last_location:
                destination = self.scheduled_locations[count + 1].base_place
                # print("not last location")
                break
            elif is_last_location:
                return None, None
        for transport in self.transport:
            if transport.is_edge_for(scheduled_origin.base_place, destination):
                origin_to_destination_transport = transport
        time = origin_to_destination_transport.get_time_transport_to(destination)
        mode = origin_to_destination_transport.get_mode_transport_to(destination)
        return time, mode
