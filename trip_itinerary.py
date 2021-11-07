from day_itinerary import DayItinerary
import datetime


class TripItinerary:
    def __init__(self, start_date: datetime.datetime, end_date: datetime.datetime, days_itinerary: [DayItinerary] = None):
        self.days_itinerary = {}
        self.start_date = start_date
        self.current_date = start_date
        self.end_date = end_date
        self.trip_days = (end_date - start_date).days + 1
        self.nonvisted_locations = None
        if days_itinerary:
            self.add_day_itinerary(days_itinerary)

    def add_day_itinerary(self, day_schedule: DayItinerary):
        if isinstance(day_schedule, (list, set, tuple)):
            for schedule in day_schedule:
                self.days_itinerary[schedule.start_date_time.strftime('%Y-%m-%d')] = day_schedule
        else:
            self.days_itinerary[day_schedule.start_date_time.strftime('%Y-%m-%d')] = day_schedule

    def next_day(self):
        self.current_date += datetime.timedelta(days=1)

    def add_nonvisited_locations(self, places: set):
        self.nonvisted_locations = places
