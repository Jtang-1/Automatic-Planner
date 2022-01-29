from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_session import Session
from website import website_helpers
from datetime import timedelta
import secrets
import copy
from place_model.place import Place
from website import modify_graph
import shortest_path
from trip_itinerary import TripItinerary
from day_itinerary import DayItinerary
import datetime
import jsonpickle
import redis
from place_model.home import Home

from place_model import google_map_distance_matrix as dist_matrix

# http://127.0.0.1:5000
app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)

#Configure Redis
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

server_session = Session(app)

@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route("/", methods=["POST", "GET"])
def home():
    locations = []
    if "location_name" not in session:
        session["location_name"] = []
        session["place_id"] = []
        session["location"] = []
        session["place_visiting_name"] = None
        session["home"] = None
        session["new_destination"] = None
        session["places"] = []
        session["is_new_destination"] = False
        record_inputs_changed()

    else:
        for location in session["location"]:
            locations.append(jsonpickle.decode(location, keys=True))
    if "place_visiting_lat_lng" not in session:
        session["place_visiting_lat_lng"] = {"lat": None, "lng": None}
    return render_template("home.html", locations=zip(session["location_name"], session["place_id"], locations),
                           map_locations=zip(session["location_name"], session["place_id"], locations),
                           visit_place_lat=session["place_visiting_lat_lng"]["lat"],
                           visit_place_lng=session["place_visiting_lat_lng"]["lng"],
                           visit_place=session["place_visiting_name"])


@app.route("/receiveDestination", methods=["POST"])
def receiveDestination():
    if request.method == "POST":
        print("in receive destination")
        record_inputs_changed()
        place_details = request.get_json(force=True)
        print("place_details is", place_details)
        new_place = modify_graph.create_attraction(place_details, session["visit_hours"])
        print("session value of new desitation in receive Destination is,", session["is_new_destination"])
        print('place id session contains', session["place_id"])
        print('new place place id is', new_place.place_id)
        print('is new place place id in session', new_place.place_id in session["place_id"])
        if new_place.place_id in session["place_id"]:
            session["is_new_destination"] = False
        if new_place.place_id not in session["place_id"]:
            print("setting new destination as true new destination")
            session["new_destination"] = jsonpickle.encode(new_place)
            session["is_new_destination"] = True
            session["places"].append(jsonpickle.encode(new_place, keys=True))
            session.modified = True
        process_place(new_place)
        print("in receive destination location names in session are", session["location_name"])
    return jsonify({'result': 'Success!'})


@app.route("/loadNewDestinationMapData", methods=["GET"])
def loadNewDestinationMapData():
    print("session is new destionation value is", session["is_new_destination"])
    new_destination = jsonpickle.decode(session["new_destination"])
    if isinstance(new_destination, Home):
        return None
    elif not session["is_new_destination"]:
        return None
    else:
        new_destination_name = new_destination.name
        new_destination_lat_lng = [new_destination.lat, new_destination.lng]
        print("new desintation from load call is", new_destination.name)
        return jsonify(new_destination_name=new_destination_name,
                       new_destination_lat_lng=new_destination_lat_lng)


@app.route("/receiveVisitHours", methods=["POST"])
def receiveVisitHours():
    if request.method == "POST":
        record_inputs_changed()
        visit_hours = request.get_json(force=True)
        session["visit_hours"] = visit_hours
        print('in receiveVisit Hours')
    return jsonify({'result': 'Success!'})


@app.route("/receiveHome", methods=["POST"])
def receiveHome():
    if request.method == "POST":
        record_inputs_changed()
        place_details = request.get_json(force=True)
        new_home = modify_graph.create_home(place_details)
        print("in receive home, place id of home is", new_home.place_id)
        process_place(new_home)
        session["places"].append(jsonpickle.encode(new_home, keys=True))
    return jsonify({'result': 'Success!'})


@app.route("/loadHomeMapData", methods=["GET"])
def loadHomeMapData():
    if session["home"]:
        session_home = jsonpickle.decode(session["home"])
        home_name = session_home.name
        home_lat_lng = [session_home.lat, session_home.lng]
        print(home_lat_lng, "this is home_lat_lng")
        return jsonify(home_name=home_name, home_lat_lng=home_lat_lng)

@app.route("/removeHome", methods=["POST"])
def removeHome():
    if request.method == "POST":
        print("in session home is", session["home"])
        if session["home"]:
            home_place_id = jsonpickle.decode(session["home"]).place_id
            home_place_id_index = session["place_id"].index(home_place_id)
            remove_place(home_place_id)
            session["home"] = None
            return jsonify({'result': 'Success!', 'index': home_place_id_index})
    return jsonify({'result': 'Success!'})

@app.route("/receiveStartDate", methods=["POST"])
def receiveStartDate():
    if request.method == "POST":
        if "start_date" not in session:
            record_inputs_changed()
        start_date = request.get_json(force=True)["start_date"]
        year = int(start_date.split("-")[0])
        month = int(start_date.split("-")[1])
        day = int(start_date.split("-")[2])
        start_date = datetime.datetime(year, month, day)
        session["start_date"] = jsonpickle.encode(start_date)
    return jsonify({'result': 'Success!'})


@app.route("/loadStartDate", methods=["GET"])
def loadStartDate():
    iso_start_date_str = jsonpickle.decode(session["start_date"]).strftime("%Y-%m-%d")
    return jsonify(iso_start_date_str=iso_start_date_str)


@app.route("/receiveEndDate", methods=["POST"])
def receiveEndDate():
    if request.method == "POST":
        if "end_date" not in session:
            record_inputs_changed()
        end_date = request.get_json(force=True)["end_date"]
        year = int(end_date.split("-")[0])
        month = int(end_date.split("-")[1])
        day = int(end_date.split("-")[2])
        end_date = datetime.datetime(year, month, day)
        session["end_date"] = jsonpickle.encode(end_date)
    return jsonify({'result': 'Success!'})


@app.route("/loadEndDate", methods=["GET"])
def loadEndDate():
    iso_end_date_str = jsonpickle.decode(session["end_date"]).strftime("%Y-%m-%d")
    print("iso_end_date_str is", iso_end_date_str)
    return jsonify(iso_end_date_str=iso_end_date_str)


@app.route("/receiveDayStartTime", methods=["POST"])
def receiveDayStartTime():
    if request.method == "POST":
        if "start_time" not in session:
            record_inputs_changed()
        start_time = request.get_json(force=True)["leave_time"]
        hour = int(start_time.split(":")[0])
        minute = int(start_time.split(":")[1])
        start_time = datetime.time(hour, minute)
        print("start time is created", start_time)
        session["start_time"] = jsonpickle.encode(start_time)
    return jsonify({'result': 'Success!'})


@app.route("/receiveDayEndTime", methods=["POST"])
def receiveDayEndTime():
    if request.method == "POST":
        if "end_time" not in session:
            record_inputs_changed()
        end_time = request.get_json(force=True)["return_time"]
        hour = int(end_time.split(":")[0])
        minute = int(end_time.split(":")[1])
        end_time = datetime.time(hour, minute)
        print("end time is created", end_time)
        session["end_time"] = jsonpickle.encode(end_time)
    return jsonify({'result': 'Success!'})


@app.route("/receiveVisitingArea", methods=["POST"])
def receiveVisitingArea():
    if request.method == "POST":
        place_details = request.get_json(force=True)
        print("place details is", place_details)
        print("visitng place before change is,", session["place_visiting_name"])
        session["place_visiting_name"] = place_details["name"]
        place_lat_lng = place_details["geometry"]["location"]
        session["place_visiting_lat_lng"] = place_lat_lng
    return jsonify({'result': 'Success!'})

@app.route("/loadVisitingArea", methods=["GET"])
def loadVisitingArea():
    lat = session["place_visiting_lat_lng"]["lat"]
    lng = session["place_visiting_lat_lng"]["lng"]
    return jsonify(lat=lat, lng=lng)

@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
        print("checkbox value is", request.form.get("drivingAllowance"))
        if request.form.get("drivingAllowance") == "avoidDriving":
            if "driving_allowance" in session and session["driving_allowance"]:
                record_inputs_changed()
            session["driving_allowance"] = False
        else:
            if "driving_allowance" in session and not session["driving_allowance"]:
                record_inputs_changed()
            session["driving_allowance"] = True
        print("were inputs changed?", session["inputs_changed"])
        if session["inputs_changed"]:
            graph = modify_graph.get_graph()
            graph.clear_graph()
            for encoded_place in session["location"]:
                place = jsonpickle.decode(encoded_place, keys=True)
                modify_graph.add_place(place)
                modify_graph.add_edges(place)
            itinerary = create_trip_itinerary()
            itinerary = shortest_path.create_itinerary(itinerary)
            session["itinerary"] = jsonpickle.encode(itinerary)
            for day_itinerary in itinerary.days_itinerary.values():
                current_day_of_week = day_itinerary.day_of_week
                print("current_day_of_week is", current_day_of_week)
                print(list([count, location.name, location.visit_minutes, day_itinerary.current_date_time.time(), location.open_times, location.close_times] for count, location in enumerate(day_itinerary.scheduled_locations)))
                print(list([count, location.name, location.arrive_time, location.visit_minutes, location.leave_time, day_itinerary.current_date_time.time()] for count,location in enumerate(day_itinerary.scheduled_locations)))
            print("unvisited locations are")
            print(list([location.name] for location in itinerary.nonvisted_locations))
            print("itinerary is saved")
            print("itinerary is", session["itinerary"])
            session["inputs_changed"] = False
        return redirect(url_for("results"))
    # fix so saved itinerary is just the needed info, without the objects since objects can't be converted correctly to JSON
    if request.method == "GET":
        print("in GET of results")
        pass
    print("session[inputs changed] is", session["inputs_changed"])
    return render_template("results.html", itinerary=jsonpickle.decode(session["itinerary"]))

#
# @app.route("/results_test", methods=["GET", "POST"])
# def results_test():
#     start_date_test = datetime.datetime(2022, 12, 2)
#     end_date_test = datetime.datetime(2022, 12, 15)
#     start_time_test = datetime.time(4)
#     end_time_test = datetime.time(18)
#     print("checkbox value is", request.form.get("drivingAllowance"))
#     if request.form.get("drivingAllowance") == "avoidDriving":
#         session["driving_allowance"] = False
#     else:
#         session["driving_allowance"] = True
#     trip_itinerary = create_trip_itinerary_test(start_date_test,end_date_test, start_time_test, end_time_test )
#     trip_itinerary = shortest_path.create_itinerary(trip_itinerary)
#     return render_template("results.html", itinerary=trip_itinerary)


@app.route("/removeLocation", methods=["POST"])
def removeLocation():
    if request.method == "POST":
        place_id = request.get_json(force=True)["place_ID"]
        print("location place_id is", place_id)
        place_id_index = session["place_id"].index(place_id)
        remove_place(place_id)
        record_inputs_changed()
    return jsonify({'result': 'Success!', 'index': place_id_index})


@app.route("/removeAllDestinations", methods=["POST"])
def removeAllDestinations():
    if request.method == "POST":
        removeHome();
        place_ids = copy.deepcopy(session["place_id"])
        for place_id in place_ids:
            remove_place(place_id)
    return jsonify({'result': 'Success!'})

@app.route("/getLocationIndex", methods=["POST"])
def getLocationIndex():
    if request.method == "POST":
        place_id = request.get_json(force=True)["place_ID"]
        print("getLocationcation place_id is", place_id)
        place_id_index = session["place_id"].index(place_id)
    return jsonify({'result': 'Success!', 'index': place_id_index})

def record_inputs_changed():
    print("inputs were changed")
    session["inputs_changed"] = True

def process_place(new_place: Place):
    print("in process_place. place is id", new_place.place_id)
    print(" in proces_place session place id contains", session["place_id"])
    print("in process place is new_place id in session", new_place.place_id in session["place_id"])
    if new_place.place_id not in session["place_id"]:
        session["location"].append(jsonpickle.encode(new_place, keys=True))
        # modify_graph.add_place(new_place)
        # modify_graph.add_edges(new_place)
        session["place_id"].append(new_place.place_id)
        session["location_name"].append(new_place.name)
        if new_place.place_type == "home":
            session["home"] = jsonpickle.encode(new_place)
    print("in process_place after if session place id contains", session["place_id"])


def remove_place(place_id: str):
    place_id_index = session["place_id"].index(place_id)
    print("place id index is", place_id_index)
    print("location  name is", session["location_name"][place_id_index])
    # remove_place_from_graph(session["place_id"][place_id_index])
    del session["location_name"][place_id_index]
    del session["place_id"][place_id_index]
    del session["location"][place_id_index]
    for place in session["location_name"]:
        print("in removeLocation, places left are", place)


def remove_place_from_graph(place_id: str):
    graph = modify_graph.get_graph()
    for place in graph.vertices:
        print("place is", place.name)
        if place.place_id == place_id:
            place_to_remove = place
            print("place to remove is", place_to_remove.name)
            break
    graph.remove_vertex(place_to_remove)
    for place in graph.vertices:
        print("remaining places are", place.name)


def create_trip_itinerary() -> TripItinerary:
    start_date = jsonpickle.decode(session["start_date"])
    end_date = jsonpickle.decode(session["end_date"])
    trip_itinerary = TripItinerary(start_date=start_date, end_date=end_date)
    trip_itinerary.set_is_driving_allowed(session["driving_allowance"])

    start_time_delta = website_helpers.time_to_minutesdelta(jsonpickle.decode(session["start_time"]))
    end_time_delta = website_helpers.time_to_minutesdelta(jsonpickle.decode(session["end_time"]))

    for _ in range(trip_itinerary.trip_days):
        start_date_time = trip_itinerary.current_date + start_time_delta
        end_date_time = trip_itinerary.current_date + end_time_delta
        trip_itinerary.add_day_itinerary(DayItinerary(start_date_time, end_date_time, trip_itinerary.is_driving_allowed))
        trip_itinerary.next_day()

    return trip_itinerary


def create_trip_itinerary_test(start_date, end_date, start_time, end_time) -> TripItinerary:
    trip_itinerary = TripItinerary(start_date=start_date, end_date=end_date)
    trip_itinerary.set_is_driving_allowed(True)

    start_time_delta = website_helpers.time_to_minutesdelta(start_time)
    end_time_delta = website_helpers.time_to_minutesdelta(end_time)
    create_places_test()
    for _ in range(trip_itinerary.trip_days):
        start_date_time = trip_itinerary.current_date + start_time_delta
        end_date_time = trip_itinerary.current_date + end_time_delta
        trip_itinerary.add_day_itinerary(DayItinerary(start_date_time, end_date_time, trip_itinerary.is_driving_allowed))
        trip_itinerary.next_day()

    return trip_itinerary

def create_places_test():
    Lowell_details = {'name': 'Lowell High School', 'place_id': 'ChIJLbVZeqN9j4AR_U7DEiiHSNY', 'formatted_address': '1101 Eucalyptus Dr, San Francisco, CA 94132, USA', 'type': ['secondary_school', 'school', 'point_of_interest', 'establishment'], 'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 37.73044219999999, 'lng': -122.4825763}, 'viewport': {'south': 37.72932161970851, 'west': -122.48334755, 'north': 37.7320195802915, 'east': -122.48026255}}}
    SanTung_details = {'name': 'San Tung', 'place_id': 'ChIJVwLhg12HhYARcIdFDox3HxM', 'formatted_address': '1031 Irving St, San Francisco, CA 94122, USA', 'type': ['restaurant', 'food', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 0, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 0, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 0, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 1, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 1, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 1, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 1, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 4, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 4, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 4, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 4, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 5, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 5, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 5, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 5, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 6, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 6, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 6, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 6, 'time': '1630', 'hours': 16, 'minutes': 30}}], 'weekday_text': ['Monday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Friday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Saturday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Sunday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM']}, 'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 37.7637594, 'lng': -122.4690005}, 'viewport': {'south': 37.7624988197085, 'west': -122.4703600302915, 'north': 37.7651967802915, 'east': -122.4676620697085}}}
    Golden_gate_park_details = {'name': 'Golden Gate Park', 'place_id': 'ChIJY_dFYHKHhYARMKc772iLvnE', 'formatted_address': 'San Francisco, CA, USA', 'type': ['park', 'tourist_attraction', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000', 'hours': 0, 'minutes': 0}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 37.7694208, 'lng': -122.4862138}, 'viewport': {'south': 37.75889404999999, 'west': -122.5397573, 'north': 37.77992305, 'east': -122.4243929}}}
    # Twin_peaks_details = {'name': 'Twin Peaks', 'place_id': 'ChIJt3HwrOJ9j4ARbW6uAcmhz7I', 'formatted_address': '501 Twin Peaks Blvd, San Francisco, CA 94114, USA', 'type': ['park', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 1, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 0, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 2, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 1, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 3, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 2, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 4, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 3, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 5, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 4, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 6, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 5, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 0, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 6, 'time': '0500', 'hours': 5, 'minutes': 0}}], 'weekday_text': ['Monday: 5:00 AM – 12:00 AM', 'Tuesday: 5:00 AM – 12:00 AM', 'Wednesday: 5:00 AM – 12:00 AM', 'Thursday: 5:00 AM – 12:00 AM', 'Friday: 5:00 AM – 12:00 AM', 'Saturday: 5:00 AM – 12:00 AM', 'Sunday: 5:00 AM – 12:00 AM']}, 'business_status': 'OPERATIONAL'}
    # Lands_end_details = {'name': 'Lands End Lookout', 'place_id': 'ChIJud4Rs7KHhYARZX7u45tQsjA', 'formatted_address': '680 Point Lobos Ave, San Francisco, CA 94121, USA', 'type': ['tourist_attraction', 'travel_agency', 'park', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 0, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 1, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 1, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 5, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 5, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 6, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 6, 'time': '0900', 'hours': 9, 'minutes': 0}}], 'weekday_text': ['Monday: 9:00 AM – 5:00 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: Closed', 'Friday: 9:00 AM – 5:00 PM', 'Saturday: 9:00 AM – 5:00 PM', 'Sunday: 9:00 AM – 5:00 PM']}, 'business_status': 'OPERATIONAL'}
    # Hmart_details = {'name': 'H Mart San Francisco', 'place_id': 'ChIJ7aBXZ6F9j4ARIwdM6ks0JgE', 'formatted_address': '3995 Alemany Blvd, San Francisco, CA 94132, USA', 'type': ['grocery_or_supermarket', 'food', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 0, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 1, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 1, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 2, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 2, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 3, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 3, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 4, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 4, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 5, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 5, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 6, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 6, 'time': '0800', 'hours': 8, 'minutes': 0}}], 'weekday_text': ['Monday: 8:00 AM – 10:00 PM', 'Tuesday: 8:00 AM – 10:00 PM', 'Wednesday: 8:00 AM – 10:00 PM', 'Thursday: 8:00 AM – 10:00 PM', 'Friday: 8:00 AM – 10:00 PM', 'Saturday: 8:00 AM – 10:00 PM', 'Sunday: 8:00 AM – 10:00 PM']}, 'business_status': 'OPERATIONAL'}

    Lowell = modify_graph.create_home(Lowell_details)
    SanTung = modify_graph.create_attraction(SanTung_details, 2)
    Golden_gate_park = modify_graph.create_attraction(Golden_gate_park_details, 20)
    # Twin_peaks = modify_graph.create_attraction(Twin_peaks_details, 1)
    # Lands_end = modify_graph.create_attraction(Lands_end_details, 6)
    # Hmart = modify_graph.create_attraction(Hmart_details, 1)

    process_place_test(Lowell)
    process_place_test(SanTung)
    process_place_test(Golden_gate_park)
    # process_place_test(Twin_peaks)
    # process_place_test(Lands_end)
    # process_place_test(Hmart)

def process_place_test(new_place: Place):
    modify_graph.add_place(new_place)
    modify_graph.add_edges(new_place)


if __name__ == "__main__":
    test = False

    test_LA = False
    test_SF = True

    if test:
        start_date_test = datetime.datetime(2022, 12, 2)
        end_date_test = datetime.datetime(2022, 12, 6)
        start_time_test = datetime.time(4)
        end_time_test = datetime.time(18)

        if test_LA:
            UCI_details = {'name': 'University of California Irvine', 'place_id': 'ChIJkb-SJQ7e3IAR7LfattDF-3k', 'formatted_address': 'Irvine, CA 92697, USA', 'type': ['university', 'point_of_interest', 'establishment'], 'business_status': 'OPERATIONAL'}
            #6
            Great_Park_details = {'name': 'Great Park Ice & Fivepoint Arena', 'place_id': 'ChIJgbGAbmLD3IARw5nd_Msw7RM', 'formatted_address': '888 Ridge Valley, Irvine, CA 92618, USA', 'type': ['point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 0, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 1, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 1, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 2, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 2, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 3, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 3, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 4, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 4, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 5, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 5, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 6, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 6, 'time': '0600', 'hours': 6, 'minutes': 0}}], 'weekday_text': ['Monday: 6:00 AM – 11:00 PM', 'Tuesday: 6:00 AM – 11:00 PM', 'Wednesday: 6:00 AM – 11:00 PM', 'Thursday: 6:00 AM – 11:00 PM', 'Friday: 6:00 AM – 11:00 PM', 'Saturday: 6:00 AM – 11:00 PM', 'Sunday: 6:00 AM – 11:00 PM']}, 'business_status': 'OPERATIONAL'}
            #10
            Spectrum_details = {'name': 'Irvine Spectrum Center', 'place_id': 'ChIJR892-fvn3IARQnnqgTu-Phc', 'formatted_address': '670 Spectrum Center Dr, Irvine, CA 92618, USA', 'type': ['shopping_mall', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 0, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 1, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 1, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 2, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 2, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 3, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 3, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 4, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 4, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 5, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 5, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 6, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 6, 'time': '1000', 'hours': 10, 'minutes': 0}}], 'weekday_text': ['Monday: 10:00 AM – 9:00 PM', 'Tuesday: 10:00 AM – 9:00 PM', 'Wednesday: 10:00 AM – 9:00 PM', 'Thursday: 10:00 AM – 9:00 PM', 'Friday: 10:00 AM – 10:00 PM', 'Saturday: 10:00 AM – 10:00 PM', 'Sunday: 10:00 AM – 9:00 PM']}, 'business_status': 'OPERATIONAL'}
            #8
            Disneyland_details= {'name': 'Disneyland Park', 'place_id': 'ChIJa147K9HX3IAR-lwiGIQv9i4', 'formatted_address': '1313 Disneyland Dr, Anaheim, CA 92802, USA', 'type': ['tourist_attraction', 'amusement_park', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 0, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 1, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 1, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 2, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 2, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 3, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 3, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 4, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 4, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 5, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 5, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 6, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 6, 'time': '0800', 'hours': 8, 'minutes': 0}}], 'weekday_text': ['Monday: 8:00 AM – 11:00 PM', 'Tuesday: 8:00 AM – 11:00 PM', 'Wednesday: 8:00 AM – 11:00 PM', 'Thursday: 8:00 AM – 11:00 PM', 'Friday: 8:00 AM – 11:00 PM', 'Saturday: 8:00 AM – 11:00 PM', 'Sunday: 8:00 AM – 11:00 PM']}, 'business_status': 'OPERATIONAL'}
            #11
            Southcoast_details = {'name': 'South Coast Plaza', 'place_id': 'ChIJCyDHJSXf3IAR2DBM02jy2dE', 'formatted_address': '3333 Bristol St, Costa Mesa, CA 92626, USA', 'type': ['shopping_mall', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '1900', 'hours': 19, 'minutes': 0}, 'open': {'day': 0, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 1, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 1, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 2, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 2, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 3, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 3, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 4, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 4, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 5, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 5, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 6, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 6, 'time': '1100', 'hours': 11, 'minutes': 0}}], 'weekday_text': ['Monday: 11:00 AM – 8:00 PM', 'Tuesday: 11:00 AM – 8:00 PM', 'Wednesday: 11:00 AM – 8:00 PM', 'Thursday: 11:00 AM – 8:00 PM', 'Friday: 11:00 AM – 8:00 PM', 'Saturday: 11:00 AM – 8:00 PM', 'Sunday: 11:00 AM – 7:00 PM']}, 'business_status': 'OPERATIONAL'}
            #10
            Costco_details = {'name': 'Costco Wholesale', 'place_id': 'ChIJYa9Pxlbd3IARpbubX7xROaQ', 'formatted_address': '115 Technology Dr, Irvine, CA 92618, USA', 'type': ['department_store', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '1800', 'hours': 18, 'minutes': 0}, 'open': {'day': 0, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 1, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 1, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 2, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 2, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 3, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 3, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 4, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 4, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 5, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 5, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 6, 'time': '1800', 'hours': 18, 'minutes': 0}, 'open': {'day': 6, 'time': '0930', 'hours': 9, 'minutes': 30}}], 'weekday_text': ['Monday: 10:00 AM – 8:30 PM', 'Tuesday: 9:00 AM – 8:30 PM', 'Wednesday: 10:00 AM – 8:30 PM', 'Thursday: 9:00 AM – 8:30 PM', 'Friday: 10:00 AM – 8:30 PM', 'Saturday: 9:30 AM – 6:00 PM', 'Sunday: 10:00 AM – 6:00 PM']}, 'business_status': 'OPERATIONAL'}
            Mcdonald_details ={'name': "McDonald's", 'place_id': 'ChIJHZJ7UqHd3IARXzrKFEIBFyk', 'formatted_address': '5445 Alton Pkwy, Irvine, CA 92614, USA', 'type': ['cafe', 'restaurant', 'food', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000', 'hours': 0, 'minutes': 0}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'business_status': 'OPERATIONAL'}
            MET_details = {'name': 'The Metropolitan Museum of Art', 'place_id': 'ChIJb8Jg9pZYwokR-qHGtvSkLzs', 'formatted_address': '1000 5th Ave, New York, NY 10028, USA', 'type': ['art_gallery', 'tourist_attraction', 'museum', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 0, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 1, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 1, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 2, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 2, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 4, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 4, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 5, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 5, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 6, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 6, 'time': '1000', 'hours': 10, 'minutes': 0}}], 'weekday_text': ['Monday: 10:00 AM – 5:00 PM', 'Tuesday: 10:00 AM – 5:00 PM', 'Wednesday: Closed', 'Thursday: 10:00 AM – 5:00 PM', 'Friday: 10:00 AM – 9:00 PM', 'Saturday: 10:00 AM – 9:00 PM', 'Sunday: 10:00 AM – 5:00 PM']}, 'business_status': 'OPERATIONAL'}
            Sharkeez_details = {'name': 'Baja Sharkeez', 'place_id': 'ChIJvxBa4_4f3YARih5A9O_Z6ps', 'formatted_address': '114 Mc Fadden Pl, Newport Beach, CA 92663, USA', 'type': ['restaurant', 'bar', 'food', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 1, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 0, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 2, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 1, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 3, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 2, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 4, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 3, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 5, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 4, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 6, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 5, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 0, 'time': '0200', 'hours': 2, 'minutes': 0}, 'open': {'day': 6, 'time': '0900', 'hours': 9, 'minutes': 0}}], 'weekday_text': ['Monday: 11:00 AM – 2:00 AM', 'Tuesday: 11:00 AM – 2:00 AM', 'Wednesday: 11:00 AM – 2:00 AM', 'Thursday: 11:00 AM – 2:00 AM', 'Friday: 11:00 AM – 2:00 AM', 'Saturday: 9:00 AM – 2:00 AM', 'Sunday: 9:00 AM – 2:00 AM']}, 'business_status': 'OPERATIONAL'}

            UCI = modify_graph.create_home(UCI_details)
            Great_Park = modify_graph.create_attraction(Great_Park_details, 1)
            Spectrum = modify_graph.create_attraction(Spectrum_details, 2)
            Disneyland = modify_graph.create_attraction(Disneyland_details, 1)
            Southcoast = modify_graph.create_attraction(Southcoast_details, 6)
            Costco = modify_graph.create_attraction(Costco_details, 1)
            Mcdonald = modify_graph.create_attraction(Mcdonald_details, 1)
            MET = modify_graph.create_attraction(MET_details, 1)
            Sharkeez = modify_graph.create_attraction(Sharkeez_details, 2)

            process_place_test(UCI)
            process_place_test(Great_Park)
            process_place_test(Spectrum)
            process_place_test(Disneyland)
            process_place_test(Southcoast)
            process_place_test(Costco)
            process_place_test(Mcdonald)
            process_place_test(MET)
            process_place_test(Sharkeez)

        elif test_SF:
            Lowell_details = {'name': 'Lowell High School', 'place_id': 'ChIJLbVZeqN9j4AR_U7DEiiHSNY', 'formatted_address': '1101 Eucalyptus Dr, San Francisco, CA 94132, USA', 'type': ['secondary_school', 'school', 'point_of_interest', 'establishment'], 'business_status': 'OPERATIONAL'}
            SanTung_details = {'name': 'San Tung', 'place_id': 'ChIJVwLhg12HhYARcIdFDox3HxM', 'formatted_address': '1031 Irving St, San Francisco, CA 94122, USA', 'type': ['restaurant', 'food', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 0, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 0, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 0, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 1, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 1, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 1, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 1, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 4, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 4, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 4, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 4, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 5, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 5, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 5, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 5, 'time': '1630', 'hours': 16, 'minutes': 30}}, {'close': {'day': 6, 'time': '1500', 'hours': 15, 'minutes': 0}, 'open': {'day': 6, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 6, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 6, 'time': '1630', 'hours': 16, 'minutes': 30}}], 'weekday_text': ['Monday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Friday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Saturday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM', 'Sunday: 11:00 AM – 3:00 PM, 4:30 – 8:30 PM']}, 'business_status': 'OPERATIONAL'}
            Golden_gate_park_details = {'name': 'Golden Gate Park', 'place_id': 'ChIJY_dFYHKHhYARMKc772iLvnE', 'formatted_address': 'San Francisco, CA, USA', 'type': ['park', 'tourist_attraction', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000', 'hours': 0, 'minutes': 0}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'business_status': 'OPERATIONAL'}
            # Twin_peaks_details = {'name': 'Twin Peaks', 'place_id': 'ChIJt3HwrOJ9j4ARbW6uAcmhz7I', 'formatted_address': '501 Twin Peaks Blvd, San Francisco, CA 94114, USA', 'type': ['park', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 1, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 0, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 2, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 1, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 3, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 2, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 4, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 3, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 5, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 4, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 6, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 5, 'time': '0500', 'hours': 5, 'minutes': 0}}, {'close': {'day': 0, 'time': '0000', 'hours': 0, 'minutes': 0}, 'open': {'day': 6, 'time': '0500', 'hours': 5, 'minutes': 0}}], 'weekday_text': ['Monday: 5:00 AM – 12:00 AM', 'Tuesday: 5:00 AM – 12:00 AM', 'Wednesday: 5:00 AM – 12:00 AM', 'Thursday: 5:00 AM – 12:00 AM', 'Friday: 5:00 AM – 12:00 AM', 'Saturday: 5:00 AM – 12:00 AM', 'Sunday: 5:00 AM – 12:00 AM']}, 'business_status': 'OPERATIONAL'}
            # Lands_end_details = {'name': 'Lands End Lookout', 'place_id': 'ChIJud4Rs7KHhYARZX7u45tQsjA', 'formatted_address': '680 Point Lobos Ave, San Francisco, CA 94121, USA', 'type': ['tourist_attraction', 'travel_agency', 'park', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 0, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 1, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 1, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 5, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 5, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 6, 'time': '1700', 'hours': 17, 'minutes': 0}, 'open': {'day': 6, 'time': '0900', 'hours': 9, 'minutes': 0}}], 'weekday_text': ['Monday: 9:00 AM – 5:00 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: Closed', 'Friday: 9:00 AM – 5:00 PM', 'Saturday: 9:00 AM – 5:00 PM', 'Sunday: 9:00 AM – 5:00 PM']}, 'business_status': 'OPERATIONAL'}
            # Hmart_details = {'name': 'H Mart San Francisco', 'place_id': 'ChIJ7aBXZ6F9j4ARIwdM6ks0JgE', 'formatted_address': '3995 Alemany Blvd, San Francisco, CA 94132, USA', 'type': ['grocery_or_supermarket', 'food', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 0, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 1, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 1, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 2, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 2, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 3, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 3, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 4, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 4, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 5, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 5, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 6, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 6, 'time': '0800', 'hours': 8, 'minutes': 0}}], 'weekday_text': ['Monday: 8:00 AM – 10:00 PM', 'Tuesday: 8:00 AM – 10:00 PM', 'Wednesday: 8:00 AM – 10:00 PM', 'Thursday: 8:00 AM – 10:00 PM', 'Friday: 8:00 AM – 10:00 PM', 'Saturday: 8:00 AM – 10:00 PM', 'Sunday: 8:00 AM – 10:00 PM']}, 'business_status': 'OPERATIONAL'}

            Lowell = modify_graph.create_home(Lowell_details)
            SanTung = modify_graph.create_attraction(SanTung_details, 1)
            Golden_gate_park = modify_graph.create_attraction(Golden_gate_park_details, 2)
            # Twin_peaks = modify_graph.create_attraction(Twin_peaks_details, 1)
            # Lands_end = modify_graph.create_attraction(Lands_end_details, 6)
            # Hmart = modify_graph.create_attraction(Hmart_details, 1)

            process_place_test(Lowell)
            process_place_test(SanTung)
            process_place_test(Golden_gate_park)
            # process_place_test(Twin_peaks)
            # process_place_test(Lands_end)
            # process_place_test(Hmart)


        trip_itinerary_test = create_trip_itinerary_test(start_date_test, end_date_test, start_time_test, end_time_test)
        trip_itinerary_test = shortest_path.create_itinerary(trip_itinerary_test)

        #print("trip days is", trip_itinerary_test.trip_days)
        print("days_itinerary in Trip_itinerary", trip_itinerary_test.days_itinerary)
        for day_itinerary in trip_itinerary_test.days_itinerary.values():
            current_day_of_week = day_itinerary.day_of_week
            print("current_day_of_week is", current_day_of_week)
            print(list([count, location.name, location.visit_minutes, day_itinerary.current_date_time.time(), location.open_times, location.close_times] for count, location in enumerate(day_itinerary.scheduled_locations)))
            print(list([count, location.name, location.arrive_time, location.visit_minutes, location.leave_time, day_itinerary.current_date_time.time()] for count,location in enumerate(day_itinerary.scheduled_locations)))

        for location in trip_itinerary_test.nonvisted_locations:
            print("unvisited location is", location.name)
        if test_LA:
            remove_place_from_graph(Southcoast_details["place_id"])

    app.run(debug=True)
