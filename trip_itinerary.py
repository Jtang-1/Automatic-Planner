from day_itinerary import DayItinerary


class TripItinerary:
    def __init__(self, trip_days: int, days_itinerary: [DayItinerary] = None):
        self.days_itinerary = []
        self.trip_days = trip_days
        if days_itinerary:
            self.days_itinerary = days_itinerary

    def add_day_itinerary(self, day_schedule):
        self.days_itinerary.append(day_schedule)