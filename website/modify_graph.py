from place_model.home import Home
from place_model.edge import Edge
from place_model.place import Place
from place_model.attraction import Attraction
import place_model.google_map_distance_matrix as dist_api
from place_model.place_graph import PlaceGraph
from website.website_helpers import *

graph = PlaceGraph()


def get_graph():
    return graph


def create_home(place_details):
    opening_hours = key_value("opening_hours", place_details)
    business_status = key_value("business_status", place_details)
    lng = key_value("geometry", place_details)["location"]["lng"]
    lat = key_value("geometry", place_details)["location"]["lat"]
    return Home(place_details["place_id"], place_details["name"],lng, lat,
                opening_hours, business_status)


def create_attraction(place_details, visit_hours):
    place_type = key_value("type", place_details)
    opening_hours = key_value("opening_hours", place_details)
    business_status = key_value("business_status", place_details)
    lng = key_value("geometry", place_details)["location"]["lng"]
    lat = key_value("geometry", place_details)["location"]["lat"]
    visit_minutes = visit_hours * 60
    print("This place is created:", place_details["name"])
    return Attraction(place_details["place_id"], place_details["name"],lng, lat, place_type,
                      opening_hours, business_status, visit_minutes)


def add_place(new_place: Place):
    graph.add_vertex(new_place)


def add_edges(new_place: Place):
    distance_dict = neighboring_distances(new_place)
    # print("distance dict in add_edges is", distance_dict)
    for place in graph.vertices:
        if place != new_place:
            # print("new_place is", new_place)
            # print("place in add_edges is", place)
            dist_to_neighbor = distance_dict[place]
            graph.add_edge(Edge(place, new_place, dist_to_neighbor))
    # print(graph.num_edge)


def add_edge_transport_time(origin: Place, destination: Place, transport_time: int, transport_mode: str):
    interested_edge = graph.get_edge(origin, destination)
    interested_edge.set_info_transport_to(destination, transport_time, transport_mode)


def neighboring_distances(place: Place) -> dict[Place, int]:
    existing_places = set(graph.vertices)
    # print("Existing_places are", existing_places)
    # print("passed in place is", place)
    existing_places.remove(place)
    existing_places = list(existing_places)
    # Google Distance Matrix API Max 25 origins or 25 destinations per request
    existing_places_chunks = list(chunks(existing_places, 24))
    final_distance_dict = {}
    for existing_places_chunk in existing_places_chunks:
        if len(existing_places_chunk) != 0:
            distance_dict = dist_api.distance_dict(place, existing_places_chunk)
            final_distance_dict = final_distance_dict | distance_dict[place]
        # print("this is distance_dict", distance_dict)
    return final_distance_dict


def remove_place(place_to_remove: Place):
    graph.remove_vertex(place_to_remove)


def remove_edge(place: Place):
    pass
