from typing import Union
import math
from website import modify_graph
from place_model.place import Place
from place_model.home import Home
from trip_itinerary import TripItinerary
import datetime
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
    # print("visited places at start are", visited_places)
    visited_places = {graph.home}
    for day_plan in itinerary.days_itinerary.values():
        # print("day_plan day length is", day_plan.day_minutes / 60)
        print("visited places b/f add_day_itinerary are", visited_places)
        itinerary.add_day_itinerary(create_day_itinerary(day_plan))
        print("in create_itinerary")
        print("visited places after add_day_itinerary is", visited_places)
        if is_all_visited():
            break
    itinerary.add_nonvisited_locations(graph.vertices ^ visited_places)
    return itinerary


def create_day_itinerary(day_plan: DayItinerary) -> DayItinerary:  # will need to pass in day of the week
    add_first_destination(day_plan)
    day_shortest_route(day_plan)
    back_home(day_plan)

    # print("day itinerary is", [(count, place.name) for count, place in enumerate(day_plan.locations)])
    return day_plan


def day_shortest_route(day_plan: DayItinerary):
    global skipped_places
    total_path_connections = graph.num_vertices - len(visited_places)
    prev_place = day_plan.locations[-1]
    for _ in range(total_path_connections):
        if is_all_checked():
            break
        current_place = day_plan.locations[-1]
        next_place = closest_unvisited_not_home_neighbor(prev_place)
        if not should_visit(day_plan, current_place, next_place):
            prev_place = next_place
            continue
        add_location_to_day_itinerary(day_plan, current_place, next_place)
        prev_place = next_place
    skipped_places = set()
    # for count, place in enumerate(visit_order):
    #     print(count, place.name)



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
    print("in farthest_not_home_neighbor")
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


def add_first_destination(day_plan: DayItinerary):
    global skipped_places
    home = graph.home
    day_plan.add_place(home)
    farthest_neighbor = farthest_not_home_neighbor(home)
    total_path_connections = graph.num_vertices - len(visited_places)
    for _ in range(total_path_connections):
        if should_visit(day_plan, home, farthest_neighbor):
            add_location_to_day_itinerary(day_plan, home, farthest_neighbor)
            break
        elif is_all_checked():
            break
        farthest_neighbor = farthest_not_home_neighbor(home)
    skipped_places = set()


def back_home(day_plan: DayItinerary):
    current_location = day_plan.locations[-1]
    if isinstance(current_location, Home):
        return
    next_place_transport_minutes, next_place_transport_mode = get_shortest_transportation(day_plan, graph.home).values()
    modify_graph.add_edge_transport_time(current_location, graph.home, next_place_transport_minutes,
                                         next_place_transport_mode)
    add_location_to_day_itinerary(day_plan, current_location, graph.home)


def should_visit(day_plan: DayItinerary, current_place: Place, next_place: Place) -> bool:
    global skipped_places
    day_minutes = day_plan.day_minutes
    current_day_of_week = day_plan.day_of_week
    print("next place is", next_place.name)
    if next_place.is_closed_on(current_day_of_week):
        skipped_places.add(next_place)
        return False
    if day_plan.minutes_spent + next_place.visit_minutes > day_minutes or not is_open_during_visit(day_plan, next_place):
        skipped_places.add(next_place)
        return False
    next_place_transport_minutes, next_place_transport_mode = get_shortest_transportation(day_plan, next_place).values()
    if day_plan.minutes_spent + next_place.visit_minutes + next_place_transport_minutes > day_minutes\
            or not is_open_after_transport_during_visit(day_plan, next_place, next_place_transport_minutes):
        skipped_places.add(next_place)
        return False
    home_transport_minutes, next_place_transport_mode = get_shortest_transportation(day_plan, next_place).values()
    if day_plan.minutes_spent + next_place.visit_minutes + next_place_transport_minutes + home_transport_minutes > day_minutes:
        skipped_places.add(next_place)
        return False
    modify_graph.add_edge_transport_time(current_place, next_place, next_place_transport_minutes,
                                         next_place_transport_mode)
    return True


def is_open_during_visit(day_plan: DayItinerary, next_place: Place) -> bool:
    visit_time_delta = datetime.timedelta(minutes=next_place.visit_minutes)
    time_after_visit = (day_plan.current_date_time + visit_time_delta).time()
    current_day_of_week = day_plan.day_of_week
    next_place_open_time = next_place.open_times[current_day_of_week]
    next_place_close_time = next_place.close_times[current_day_of_week]
    if next_place_open_time < time_after_visit < next_place_close_time:
        return True
    return False


def is_open_after_transport_during_visit(day_plan: DayItinerary, next_place: Place, next_place_transport_minutes) -> bool:
    transport_time_delta = datetime.timedelta(minutes=next_place_transport_minutes)
    visit_time_delta = datetime.timedelta(minutes=next_place.visit_minutes)
    time_after_transport_and_visit = (day_plan.current_date_time + transport_time_delta + visit_time_delta).time()
    current_day_of_week = day_plan.day_of_week
    next_place_open_time = next_place.open_times[current_day_of_week]
    next_place_close_time = next_place.close_times[current_day_of_week]
    # print("in open during visit", next_place.name, "close time is", next_place_close_time,"current time is", day_plan.current_date_time.time(), "time after transport and visit is", time_after_transport_and_visit)
    if next_place_open_time < time_after_transport_and_visit < next_place_close_time:
        return True
    return False


def add_location_to_day_itinerary(day_plan: DayItinerary, current_place: Place, next_place: Place):
    add_transport_to_day_itinerary(day_plan, current_place, next_place)
    day_plan.add_place(next_place)
    day_plan.add_edge(graph.get_edge(current_place, next_place))
    if not isinstance(next_place, Home):
        visited_places.add(next_place)
        day_plan.add_minutes_spent(next_place.visit_minutes)


def add_transport_to_day_itinerary(day_plan: DayItinerary, current_place: Place, next_place: Place):
    transport_time, transport_mode = get_next_place_transport_info(day_plan, next_place).values()
    modify_graph.add_edge_transport_time(current_place, next_place, transport_time, transport_mode)
    print("current place is", current_place.name)
    print("next_place is", next_place.name)
    print("transport time is", transport_time)
    day_plan.add_minutes_spent(transport_time)


def get_shortest_transportation(day_plan: DayItinerary, next_place: Place) -> {int, str}:
    if day_plan.is_driving_allowed:
        modes = {"driving", "walking", "transit"}
    else:
        modes = {"walking", "transit"}
    print("allowed modes are", modes)
    departure_time = day_plan.current_date_time
    current_place = day_plan.locations[-1]
    if isinstance(next_place, Home):
        departure_time += datetime.timedelta(minutes=current_place.visit_minutes)
    transport_time = float('inf')
    for mode in modes:
        new_transport_time = dist_api.find_travel_time(current_place, next_place, mode, departure_time)
        if new_transport_time is not None and new_transport_time < transport_time:
            transport_time = new_transport_time
            fastest_mode = mode
    print("transport time is", transport_time)
    print("transport mode is", fastest_mode)
    return {"transport_time": math.ceil(transport_time / 60), "mode": fastest_mode}


def get_next_place_transport_info(day_plan, next_place) -> (int, str):
    current_place = day_plan.locations[-1]
    transport_edge = graph.get_edge(current_place, next_place)
    transport_time = transport_edge.get_time_transport_to(next_place)
    transport_mode = transport_edge.get_mode_transport_to(next_place)
    return {"transport_time": transport_time, "mode": transport_mode}


def is_visited(place: Place) -> bool:
    if place in visited_places or place in skipped_places:
        return True
    return False


def is_all_visited() -> bool:
    print("in is all visited, graph.num_vertices is", graph.num_vertices)
    print("len of visited places is", len(visited_places))
    print("visited places are", visited_places)
    print("graph veritcies are", graph.vertices)
    if graph.num_vertices == len(visited_places):
        return True
    return False

def is_all_checked() -> bool:
    num_places_left = graph.num_vertices - len(visited_places)
    if num_places_left == len(skipped_places):
        return True
    return False