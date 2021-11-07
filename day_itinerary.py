from place_model.place import Place
from place_model.edge import Edge
from place_model.place_graph import PlaceGraph
import datetime


class DayItinerary:
    def __init__(self, start_date_time: datetime.datetime, end_date_time: datetime.datetime,
                 locations: [Place] = None):
        self.locations = []
        self.transport = []
        self.start_date_time = start_date_time
        self.current_time = start_date_time
        self.end_date_time = end_date_time
        self.day_minutes = int((end_date_time - start_date_time).total_seconds()/60)
        if locations:
            self.locations = locations

    def add_place(self, location: Place):
        if isinstance(location, (list, set, tuple)):
            self.locations + list(location)
        else:
            self.locations.append(location)

    def add_minutes_spent(self, minutes):
        minutes_spent = datetime.timedelta(minutes = minutes)
        self.current_time += minutes_spent

    @property
    def minutes_spent(self):
        return (self.current_time - self.start_date_time).total_seconds() / 60

    @property
    def date(self):
        return self.current_time.date()

    def is_empty(self):
        if len(self.locations):
            return False
        return True

    def add_edge(self, transport: Edge):
        self.transport.append(transport)

    def transport_info_from(self, origin: Place) -> (int, str):
        print("self.transport is", self.transport)
        for count, location in enumerate(self.locations):
            is_last_location = (count == (len(self.locations)-1))
            if location == origin and not is_last_location:
                destination = self.locations[count+1]
                print("not last location")
                break
            elif is_last_location:
                return None, None
        for transport in self.transport:
            if transport.is_edge_for(origin, destination):
                print("in transport TRUE")
                origin_to_destination_transport = transport
        print("origin is", origin.name)
        print("destination is", destination.name)
        time = origin_to_destination_transport.get_time_transport_to(destination)
        mode = origin_to_destination_transport.get_mode_transport_to(destination)
        return time, mode

