from typing import Union
import math
from website import modify_graph
from place_model.place import Place
from place_model.home import Home
from trip_itinerary import TripItinerary
from place_model.place_graph import PlaceGraph
from place_model.attraction import Attraction
from day_itinerary import DayItinerary
from place_model import google_map_distance_matrix as dist_api
import copy

graph = modify_graph.get_graph()
visited_places = set()
skipped_places = set()


def create_itinerary(itinerary: TripItinerary) -> TripItinerary:
    global visited_places
    #print("visited places at start are", visited_places)
    visited_places = {graph.home}
    for day_plan in itinerary.days_itinerary.values():
        #print("day_plan day length is", day_plan.day_minutes / 60)
        itinerary.add_day_itinerary(create_day_itinerary(day_plan))
        if len(visited_places) == graph.num_vertices:
            print("visited places are", visited_places)
            break
    return itinerary


def create_day_itinerary(day_plan: DayItinerary) -> DayItinerary:  # will need to pass in day of the week
    day_plan = add_first_destination(day_plan)
    day_plan = day_shortest_route(day_plan)
    # print("day itinerary is", [(count, place.name) for count, place in enumerate(day_plan.locations)])
    return day_plan


def add_first_destination(day_plan: DayItinerary) -> DayItinerary:
    home = graph.home
    day_plan.add_place(home)
    farthest_neighbor = farthest_not_home_neighbor(home)
    add_location_to_day_itinerary(day_plan, home, farthest_neighbor)
    return day_plan

def day_shortest_route(day_plan: DayItinerary) -> DayItinerary:
    global skipped_places
    total_path_connections = graph.num_vertices - len(visited_places)
    day_minutes = day_plan.day_minutes
    prev_place = day_plan.locations[-1]
    for _ in range(total_path_connections):
        current_place = day_plan.locations[-1]
        next_place = closest_unvisited_not_home_neighbor(prev_place)
        if day_plan.minutes_spent + next_place.visit_minutes > day_minutes:
            skipped_places.add(next_place)
            prev_place = next_place
            continue
        transport_info = shortest_transportation(day_plan, next_place)
        transport_time, transport_mode = transport_info["transport_time"], transport_info["mode"]
        if day_plan.minutes_spent + next_place.visit_minutes + transport_time > day_minutes:
            skipped_places.add(next_place)
            prev_place = next_place
            continue
        print(current_place.name, "to", next_place.name, "shortest transport + time is", transport_info)
        day_plan.add_place(next_place)
        visited_places.add(next_place)
        day_plan.add_minutes_spent(next_place.visit_minutes)
        modify_graph.add_edge_transport_time(current_place, next_place, transport_time, transport_mode)
        day_plan.add_edge(graph.get_edge(current_place, next_place))
        print("edge tranport value is", graph.get_edge(current_place, next_place).get_time_transport_to(next_place))
        prev_place = next_place
    # for count, place in enumerate(visit_order):
    #     print(count, place.name)
    skipped_places = set()
    return day_plan


def shortest_transportation(day_plan: DayItinerary, next_place: Place) -> {int, str}:
    modes = {"driving", "walking", "transit"}
    departure_time = day_plan.current_time
    current_place = day_plan.locations[-1]
    transport_time = float('inf')
    for mode in modes:
        new_transport_time = dist_api.find_travel_time(current_place, next_place, mode, departure_time)
        if new_transport_time is not None and new_transport_time < transport_time:
            transport_time = new_transport_time
            fastest_mode = mode
    return {"transport_time": math.ceil(transport_time / 60), "mode": fastest_mode}


def closest_unvisited_not_home_neighbor(node: Place) -> Union[Place, Attraction]:
    # print("vertices of copies", list(graph.vertices))
    # print("closest_not_home_neighbor passed in node", node.name)
    neighbors_edges = graph.neighbors_edges(node)
    closest_neighbor_dist = float('inf')
    closest_neighbor = None
    for edge in neighbors_edges:
        node1 = edge.place1
        node2 = edge.place2
        if edge.distance > closest_neighbor_dist:
            continue
        if node1 != node and not isinstance(node1, Home) and not is_visited(node1):
            closest_neighbor = node1
        elif node2 != node and not isinstance(node2, Home) and not is_visited(node2):
            closest_neighbor = node2
        else:
            continue
        closest_neighbor_dist = edge.distance

    # print("closest neighbor", closest_neighbor.name,  closest_neighbor_dist)
    return closest_neighbor


def farthest_not_home_neighbor(node: Place) -> Union[Place, Attraction]:
    neighbors_edges = graph.neighbors_edges(node)
    farthest_neighbor_dist = 0
    farthest_neighbor = None
    for edge in neighbors_edges:
        node1 = edge.place1
        node2 = edge.place2
        if edge.distance < farthest_neighbor_dist:
            continue
        if node1 != node and not isinstance(node1, Home) and not is_visited(node1):
            farthest_neighbor = edge.place1
        elif node2 != node and not isinstance(node2, Home) and not is_visited(node2):
            farthest_neighbor = edge.place2
        else:
            continue
        farthest_neighbor_dist = edge.distance

    # print("farthest neighbor", farthest_neighbor.name, farthest_neighbor_dist)
    return farthest_neighbor


def add_location_to_day_itinerary(day_plan: DayItinerary, current_place: Place, next_place: Place) -> DayItinerary:
    day_plan = add_transport_to_day_itinerary(day_plan, current_place, next_place)
    day_plan.add_place(next_place)
    visited_places.add(next_place)
    day_plan.add_minutes_spent(next_place.visit_minutes)
    day_plan.add_edge(graph.get_edge(current_place, next_place))
    return day_plan


def add_transport_to_day_itinerary(day_plan: DayItinerary, current_place: Place, next_place: Place) -> DayItinerary:
    transport_info = shortest_transportation(day_plan, next_place)
    transport_time, transport_mode = transport_info["transport_time"], transport_info["mode"]
    modify_graph.add_edge_transport_time(current_place, next_place, transport_time, transport_mode)
    return day_plan

def is_visited(place: Place):
    if place in visited_places or place in skipped_places:
        return True
    return False
