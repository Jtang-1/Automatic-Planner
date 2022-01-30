import copy
# import config

import os
import place_model.google_map_places as places_api
from helpers import *
from place_model.place import Place
# Mcdonald Place_ID ChIJHZJ7UqHd3IARXzrKFEIBFyk
# Starbucks Place_ID ChIJzUGCDNXc3IAR4l4UZu6QGLU
import datetime
api_key = os.environ.get("AUTOMATIC_PLANNER_GOOGLE_API_KEY")
data_type = 'json'
language = 'en'


# Returns dict with {Origin:{Destination:distance},Origin...} values
def distance_dict(origins: [Place], destinations: [Place]) -> dict[Place, dict[Place, int]]:
    print("distance dict called")
    if isinstance(origins, Place):
        origins = [origins]
    if isinstance(destinations, Place):
        destinations = [destinations]

    distance_dictionary, destinations_distance = {}, {}
    json_distance_matrix = _raw_distance_matrix(origins, destinations)
    #print("json distance matrix ", json_distance_matrix)
    for origin_count, origin in enumerate(origins):
        for destination_count, destination in enumerate(destinations):
            destinations_distance[destination] = \
                json_distance_matrix["rows"][origin_count]["elements"][destination_count]["distance"]["value"]
        distance_dictionary[origin] = copy.copy(destinations_distance)
    return distance_dictionary


def find_travel_time(origin: Place, destination: Place, mode="driving", departure_time="now") -> float:
    reference_time = datetime.datetime(1970, 1, 1)
    print("origin is", origin)
    print("find_travel_time called")
    if isinstance(departure_time, datetime.datetime):
        departure_time = int((departure_time - reference_time).total_seconds())
    json_distance_matrix = _raw_distance_matrix(origin, destination, mode=mode, departure_time=departure_time)
    #print("find travel time matrix is", json_distance_matrix)
    status = json_distance_matrix["rows"][0]["elements"][0]["status"]
    if status != "OK":
        return None
    travel_time = json_distance_matrix["rows"][0]["elements"][0]["duration"]["value"]
    return travel_time


# returns api json response as dict
def _raw_distance_matrix(origins: [Place], destinations: [Place], mode="driving", departure_time="now"):
    origins_place_ids, destinations_place_ids = place_id_parameter(origins), place_id_parameter(destinations)
    endpoint = f'https://maps.googleapis.com/maps/api/distancematrix/{data_type}'
    parameters = {"origins": origins_place_ids, "destinations": destinations_place_ids,
                  "key": api_key, "mode": mode, "departure_time": departure_time}
    url = create_encoded_url(parameters, endpoint)
    return get_url_response(url)


# creates json call parameter
def place_id_parameter(places: [Place]) -> str:
    place_ids = []
    if isinstance(places, (list, set, tuple)):
        for place in places:
            place_ids.append("place_id:" + place.place_id)
    else:
        place_ids.append("place_id:" + places.place_id)
    return "|".join(place_ids)


