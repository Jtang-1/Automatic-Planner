from place_model.place import Place


class DayItinerary:
    def __init__(self, day_minutes: int, locations: [Place] = None):
        self.locations = []
        self.day_minutes = day_minutes
        self.minutes_spent = 0
        if locations:
            self.locations = locations

    def add_place(self, location: Place):
        if isinstance(location, (list, set, tuple)):
            self.locations + list(location)
        else:
            self.locations.append(location)

    def add_minutes_spent(self, minutes):
        self.minutes_spent += minutes




