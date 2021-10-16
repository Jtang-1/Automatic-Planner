from typing import Union

from website import modify_graph
from place_model.place import Place
from place_model.home import Home
from trip_itinerary import TripItinerary
from place_model.place_graph import PlaceGraph
from place_model.attraction import Attraction
from day_itinerary import DayItinerary
import copy

graph = modify_graph.get_graph()
visited_places = set()


def create_itinerary() -> TripItinerary:
    global visited_places
    itinerary = TripItinerary(trip_days=5)
    visited_places = {graph.home}
    for _ in range(itinerary.trip_days):
        print("in create_itinerary for loop")
        itinerary.add_day_itinerary(create_day_itinerary())
        if len(visited_places) == graph.num_vertices:
            print("in break, out of places, visited places are", visited_places)
            break
    return itinerary


def create_day_itinerary() -> DayItinerary:  # will need to pass in day of the week
    home = graph.home
    farthest_neighbor = farthest_not_home_neighbor(home)
    day_plan = DayItinerary(day_minutes=840, locations=[home, farthest_neighbor])
    visited_places.add(farthest_neighbor)
    print("places in graph are", [place.name for place in graph.vertices])
    print("home is", home.name)
    print("farthest neighbor is", farthest_neighbor.name)
    day_plan.add_minutes_spent(farthest_neighbor.visit_minutes)
    day_plan = day_shortest_route(day_plan)
    print("day itinerary is", [(count, place.name) for count, place in enumerate(day_plan.locations)])
    return day_plan


def day_shortest_route(day_plan: DayItinerary) -> DayItinerary:
    total_path_connections = graph.num_vertices - len(visited_places)
    day_minutes = day_plan.day_minutes
    current_place = day_plan.locations[-1]
    for _ in range(total_path_connections):
        print("in day_shortest_route for loop")
        next_place = closest_not_home_neighbor(current_place)
        if day_plan.minutes_spent + next_place.visit_minutes> day_minutes:
            break
        day_plan.add_place(next_place)
        visited_places.add(next_place)
        day_plan.add_minutes_spent(next_place.visit_minutes)
        current_place = next_place
    # for count, place in enumerate(visit_order):
    #     print(count, place.name)
    return day_plan


def closest_not_home_neighbor(node: Place) -> Union[Place, Attraction]:
    print("vertices of copies", list(graph.vertices))
    print("passed in node", node.name)
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

    print("closest neighbor", closest_neighbor.name,  closest_neighbor_dist)
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
        elif node2 != node and not isinstance(node2, Home)and not is_visited(node2):
            farthest_neighbor = edge.place2
        else:
            continue
        farthest_neighbor_dist = edge.distance

    print("farthest neighbor", farthest_neighbor.name, farthest_neighbor_dist)
    return farthest_neighbor


def is_visited(place: Place):
    if place in visited_places:
        return True
    return False