import copy
import config
import place_model.google_map_places as places_api
from helpers import *
# Mcdonald Place_ID ChIJHZJ7UqHd3IARXzrKFEIBFyk
# Starbucks Place_ID ChIJzUGCDNXc3IAR4l4UZu6QGLU

api_key = config.api_key
data_type = 'json'
language = 'en'


# Returns dict with {Origin:{Destination:distance},Origin...} values
def distance_dict(origins: [str], destinations: [str]) -> dict[str, dict[str, str]]:
    if isinstance(origins, str):
        origins = [origins]
    if isinstance(destinations, str):
        destinations = [destinations]

    distance_dictionary, destinations_distance = {}, {}
    json_distance_matrix = _raw_distance_matrix(origins, destinations)
    print("json distance ", json_distance_matrix)
    for origin_count, origin in enumerate(origins):
        for destination_count, destination in enumerate(destinations):
            destinations_distance[destination] = \
                json_distance_matrix["rows"][origin_count]["elements"][destination_count]["distance"]["value"]
        distance_dictionary[origin] = copy.deepcopy(destinations_distance)
    return distance_dictionary


# returns api json response as dict
def _raw_distance_matrix(origins: [str], destinations: [str]):
    origins_place_ids, destinations_place_ids = place_id_parameter(origins), place_id_parameter(destinations)
    endpoint = f'https://maps.googleapis.com/maps/api/distancematrix/{data_type}'
    parameters = {"origins": origins_place_ids, "destinations": destinations_place_ids,
                  "key": api_key}
    url = create_encoded_url(parameters, endpoint)
    return get_url_response(url)


# creates json call parameter
def place_id_parameter(places: [str]) -> str:
    place_ids = []
    for place in places:
        place_ids.append("place_id:" + places_api.get_place_id(place))
    return "|".join(place_ids)


