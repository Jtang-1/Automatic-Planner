from typing import Union
import math
from helpers import *
from website import modify_graph
from place_model.place import Place
from place_model.home import Home
from trip_itinerary import TripItinerary
import datetime
from place_model.attraction import Attraction
from day_itinerary import DayItinerary
from place_model import google_map_distance_matrix as dist_api

graph = modify_graph.get_graph()
itinerary_added_places = set()
skipped_places = set()
has_not_opened_places = set()


def create_itinerary(itinerary: TripItinerary) -> TripItinerary:
    global itinerary_added_places
    # print("visited places at start are", visited_places)
    itinerary_added_places = {graph.home}
    for day_plan in itinerary.days_itinerary.values():
        # print("day_plan day length is", day_plan.day_minutes / 60)
        print("places in itinerary before add day itinerary", list(location.name for location in itinerary_added_places))
        itinerary.add_day_itinerary(create_day_itinerary(day_plan))
        print("in create_itinerary")
        print("visited places after add_day_itinerary is", list(location.name for location in itinerary_added_places))
        if is_all_visited():
            break
    itinerary.add_nonvisited_locations(graph.vertices ^ itinerary_added_places)
    return itinerary


def create_day_itinerary(day_plan: DayItinerary) -> DayItinerary:  # will need to pass in day of the week
    day_plan.add_home(graph.home)
    add_first_destination(day_plan)
    day_shortest_route(day_plan)
    back_home(day_plan)

    # print("day itinerary is", [(count, base_place.place.name) for count, place in enumerate(day_plan.locations)])
    return day_plan


def day_shortest_route(day_plan: DayItinerary):
    global skipped_places
    global has_not_opened_places
    path_connections = graph.num_vertices - len(itinerary_added_places)
    total_path_connections = int((path_connections * (path_connections + 1)) / 2)
    print("total path connections is", total_path_connections)
    current_place = day_plan.scheduled_locations[-1].base_place
    next_place = closest_unvisited_not_home_neighbor(current_place)
    for _ in range(total_path_connections):
        if is_all_skipped_or_added_to_day_itinerary() or next_place is None:
            break
        if should_visit(day_plan, current_place, next_place):
            print(next_place.name, "will be added to day_shortest_route. in day_shortest_route")
            add_location_to_day_itinerary(day_plan, current_place, next_place)
            print(next_place.name, "has been added to day_shortest_route. in day_shortest_route")
            has_not_opened_places = set()
        else:
            if only_has_not_opened_places_remain():
                print("day_shortest_route,in only has not opened places remaining")
                next_place = find_has_not_opened_place_minus_wait_and_travel_time(day_plan)
                if next_place is None:
                    break
                add_location_to_day_itinerary(day_plan, current_place, next_place)
                has_not_opened_places = set()
        current_place = day_plan.scheduled_locations[-1].base_place
        next_place = closest_unvisited_not_home_neighbor(current_place)
    has_not_opened_places = set()
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
    global has_not_opened_places
    home = day_plan.home
    farthest_neighbor = farthest_not_home_neighbor(home)
    path_connections = graph.num_vertices - len(itinerary_added_places)
    total_path_connections = int((path_connections * (path_connections + 1)) / 2)
    for _ in range(total_path_connections):
        if is_all_skipped_or_added_to_day_itinerary() or farthest_neighbor is None:
            break
        print("in start of for loop of add_first_destination, farthest neighbor is", farthest_neighbor.name)
        if should_visit(day_plan, home, farthest_neighbor):
            print("location has been added to first destination")
            day_plan.scheduled_home.set_leave_time(day_plan.current_time)
            add_location_to_day_itinerary(day_plan, home, farthest_neighbor)
            break
        elif only_has_not_opened_places_remain():
            print("in only has not opened places remaining")
            day_plan.scheduled_home.set_leave_time(day_plan.current_time)
            farthest_neighbor = find_has_not_opened_place_minus_wait_and_travel_time(day_plan)
        else:
            farthest_neighbor = farthest_not_home_neighbor(home)
            continue
        has_not_opened_places = set()
    has_not_opened_places = set()
    skipped_places = set()


def back_home(day_plan: DayItinerary):
    current_location = day_plan.scheduled_locations[-1].base_place
    home = day_plan.home
    if isinstance(current_location, Home):
        return
    next_place_transport_minutes, next_place_transport_mode = get_shortest_transportation(day_plan, home).values()
    modify_graph.add_edge_transport_time(current_location, home, next_place_transport_minutes,
                                         next_place_transport_mode)
    add_location_to_day_itinerary(day_plan, current_location, home)


def should_visit(day_plan: DayItinerary, current_place: Place, next_place: Attraction) -> bool:
    global skipped_places
    global has_not_opened_places
    day_minutes = day_plan.day_minutes
    current_day_of_week = day_plan.day_of_week
    print("checking if should visit", next_place.name)
    if next_place.is_closed_on(current_day_of_week):
        print("did not visit", next_place.name, "it is closed")
        skipped_places.add(next_place)
        return False

    if day_plan.minutes_spent + next_place.visit_minutes > day_minutes:
        print("did not visit", next_place.name, "visit exceeds allocated day time, closed before end of visit")
        skipped_places.add(next_place)
        return False
    # Layered checks to avoid excess API transportation time calls
    next_place_transport_minutes, next_place_transport_mode = get_shortest_transportation(day_plan, next_place).values()
    modify_graph.add_edge_transport_time(current_place, next_place, next_place_transport_minutes,
                                         next_place_transport_mode)
    # Check place is opened by the time you arrive
    if not is_open_after_transport_start_of_visit(day_plan, next_place, next_place_transport_minutes):
        print("place added to not open", next_place.name)
        if is_has_not_opened_yet(day_plan, next_place, next_place_transport_minutes) and next_place not in has_not_opened_places:
            has_not_opened_places.add(next_place)
        # Completely closed for the day
        else:
            skipped_places.add(next_place)
        return False
    # Check enough time in day to visit
    if day_plan.minutes_spent + next_place.visit_minutes + next_place_transport_minutes > day_minutes \
            or not is_open_after_transport_end_of_visit(day_plan, next_place, next_place_transport_minutes):
        skipped_places.add(next_place)
        print("did not visit", next_place.name, "not enough time to visit after transport")

        return False
    home_transport_minutes, next_place_transport_mode = get_shortest_transportation(day_plan, next_place).values()
    # Check enough time in day to visit and get back home
    if day_plan.minutes_spent + next_place.visit_minutes + next_place_transport_minutes + home_transport_minutes > day_minutes:
        skipped_places.add(next_place)
        return False
    return True


def is_has_not_opened_yet(day_plan: DayItinerary, next_place: Attraction, next_place_transport_minutes: int) -> bool:
    current_time = day_plan.current_date_time.time()
    current_day_of_week = day_plan.day_of_week
    time_after_transport_minutes = time_to_minutes(current_time) + next_place_transport_minutes
    for next_place_open_time in next_place.open_times[current_day_of_week]:
        if time_after_transport_minutes - time_to_minutes(next_place_open_time) < 0:
            return True
    return False


# Accounts transport time
def is_open_after_transport_start_of_visit(day_plan: DayItinerary, next_place: Attraction, next_place_transport_minutes: int) -> bool:
    current_time = day_plan.current_date_time.time()
    current_day_of_week = day_plan.day_of_week
    time_after_transport_minutes = time_to_minutes(current_time) + next_place_transport_minutes
    print("next_place.open_times[current_day_of_week] is ", next_place.open_times[current_day_of_week])
    next_place_open_close_time = zip(next_place.open_times[current_day_of_week], next_place.close_times[current_day_of_week])
    for next_place_open_time, next_place_close_time in next_place_open_close_time:
        if time_to_minutes(next_place_open_time) <= time_after_transport_minutes<= time_to_minutes(next_place_close_time):
            return True
    return False


# # Does not account transport time
# def is_open_end_of_visit(day_plan: DayItinerary, next_place: Attraction) -> bool:
#     visit_time_delta = datetime.timedelta(minutes=next_place.visit_minutes)
#     time_after_visit = (day_plan.current_date_time + visit_time_delta).time()
#     current_day_of_week = day_plan.day_of_week
#     next_place_close_time = next_place.close_times[current_day_of_week]
#     if time_after_visit <= next_place_close_time:
#         return True
#     return False


# Accounts transport time
def is_open_after_transport_end_of_visit(day_plan: DayItinerary, next_place: Attraction,
                                         next_place_transport_minutes) -> bool:
    current_time = day_plan.current_date_time.time()
    current_day_of_week = day_plan.day_of_week
    time_after_transport_and_visit = time_to_minutes(current_time) + next_place_transport_minutes + next_place.visit_minutes
    next_place_open_close_time = zip(next_place.open_times[current_day_of_week],
                                     next_place.close_times[current_day_of_week])
    # print("in open during visit", next_place.name, "close time is", next_place_close_time,"current time is", day_plan.current_date_time.time(), "time after transport and visit is", time_after_transport_and_visit)
    for next_place_open_time, next_place_close_time in next_place_open_close_time:
        if time_to_minutes(next_place_open_time) <= time_after_transport_and_visit\
                <= time_to_minutes(next_place_close_time):
            return True
    return False


def add_location_to_day_itinerary(day_plan: DayItinerary, current_place: Attraction, next_place: Attraction):
    add_transport_to_day_itinerary(day_plan, current_place, next_place)
    arrive_time = day_plan.current_time
    day_plan.add_edge(graph.get_edge(current_place, next_place))
    if isinstance(next_place, Home):
        day_plan.add_home(next_place)
        day_plan.scheduled_home.set_arrive_time(arrive_time)
    else:
        itinerary_added_places.add(next_place)
        day_plan.add_minutes_spent(next_place.visit_minutes)
        leave_time = day_plan.current_time
        day_plan.add_attraction(next_place, arrive_time, leave_time)


def add_transport_to_day_itinerary(day_plan: DayItinerary, current_place: Place, next_place: Place):
    transport_time, transport_mode = get_next_place_transport_info(day_plan, next_place).values()
    modify_graph.add_edge_transport_time(current_place, next_place, transport_time, transport_mode)
    print("current place is", current_place.name)
    print("next_place is", next_place.name)
    print("transport time is", transport_time)
    day_plan.add_minutes_spent(transport_time)


def get_shortest_transportation(day_plan: DayItinerary, next_place: Place) -> {int, str}:
    print("in get_shortest_transportation")
    if day_plan.is_driving_allowed:
        modes = {"driving", "transit"}
    else:
        modes = {"walking", "transit"}
    departure_time = day_plan.current_date_time
    current_place = day_plan.scheduled_locations[-1].base_place
    if isinstance(next_place, Home):
        departure_time += datetime.timedelta(minutes=current_place.visit_minutes)
    transport_time = float('inf')
    fastest_mode = None
    for mode in modes:
        new_transport_time = dist_api.find_travel_time(current_place, next_place, mode, departure_time)
        if new_transport_time is not None and new_transport_time < transport_time:
            transport_time = new_transport_time
            fastest_mode = mode
    return {"transport_time": math.ceil(transport_time / 60), "mode": fastest_mode}


def get_next_place_transport_info(day_plan, next_place) -> (int, str):
    current_place = day_plan.scheduled_locations[-1].base_place
    transport_edge = graph.get_edge(current_place, next_place)
    transport_time = transport_edge.get_time_transport_to(next_place)
    transport_mode = transport_edge.get_mode_transport_to(next_place)
    return {"transport_time": transport_time, "mode": transport_mode}


def is_visited(place: Place) -> bool:
    if place in itinerary_added_places or place in skipped_places or place in has_not_opened_places:
        return True
    return False


def is_all_visited() -> bool:
    print("in is all visited, graph.num_vertices is", graph.num_vertices)
    print("len of visited places is", len(itinerary_added_places))
    print("visited places are", itinerary_added_places)
    print("graph vertices are", graph.vertices)
    if graph.num_vertices == len(itinerary_added_places):
        return True
    return False


def is_all_skipped_or_added_to_day_itinerary() -> bool:
    num_non_added_places = graph.num_vertices - len(itinerary_added_places)
    if num_non_added_places == len(skipped_places):
        return True
    return False


def only_has_not_opened_places_remain() -> bool:
    num_non_added_places = graph.num_vertices - len(itinerary_added_places)
    num_visited_places = len(skipped_places) + len(has_not_opened_places)
    if len(has_not_opened_places) > 0 and num_visited_places == num_non_added_places:
        return True
    return False


# Need to check if the place chosen can be visited. Travel time isn't too far, can return to hotel in time, within closing time, etc..)
def find_has_not_opened_place_minus_wait_and_travel_time(day_plan: DayItinerary) -> Place:
    shortest_time = float('inf')
    current_day_of_week = day_plan.day_of_week
    current_time_minutes = time_to_minutes(day_plan.current_time)
    current_place = day_plan.scheduled_locations[-1].base_place
    next_place = None
    final_minutes_to_shift = 0
    print("in find_has_not_opened_place_min_wait_and_travel_time, has_not opened places are", list(location.name for location in has_not_opened_places))
    for place in has_not_opened_places:
        print("in for loop of find_has_not_opened_palce_min_wait_and_travel_time, place is", place.name)
        place_transport_minutes, place_transport_mode = get_next_place_transport_info(day_plan, place).values()
        print("place_transport_minutes", place_transport_minutes)
        print("time_to_minutes(day_plan.current_time)", time_to_minutes(day_plan.current_time))
        for next_place_open_time in place.open_times[current_day_of_week]:
            print("in find_has_not_opened_place_minus_wait_and_travel_time for loop time_to_minutes(place.open_times[current_day_of_week])",
                      time_to_minutes(next_place_open_time))
            if current_time_minutes + place_transport_minutes < time_to_minutes(next_place_open_time):
                print("in find_has_not_opened_place_minus_wait_and_travel_time for loop, in if time_to_minutes(place.open_times[current_day_of_week])",
                      time_to_minutes(next_place_open_time))
                wait_and_travel_time = time_to_minutes(next_place_open_time) + \
                                       place_transport_minutes - \
                                       current_time_minutes
                minutes_to_shift = minutes_to_shift_to_place_minus_transport(day_plan, place, next_place_open_time)

                break
        #  shift day time to next open place - transporation time ? (may not pass if should visit - may have rounding error.. of open after current time + transport)
        day_plan.add_minutes_spent(minutes_to_shift)
        print("wait_and_travel_time is", wait_and_travel_time, "shortest time is", shortest_time, "<?", wait_and_travel_time < shortest_time)
        if wait_and_travel_time < shortest_time and should_visit(day_plan, current_place, place):
            next_place = place
            shortest_time = wait_and_travel_time
            final_minutes_to_shift = minutes_to_shift
        day_plan.add_minutes_spent(- minutes_to_shift)
    day_plan.add_minutes_spent(final_minutes_to_shift)
    return next_place


def minutes_to_shift_to_place_minus_transport(day_plan: DayItinerary, next_place: Place, next_place_open_time: datetime.time) -> int:
    next_place_transport_minutes, next_place_transport_mode = get_next_place_transport_info(day_plan,
                                                                                            next_place).values()
    minutes_to_shift = time_to_minutes(next_place_open_time) - next_place_transport_minutes - time_to_minutes(day_plan.current_time)
    return minutes_to_shift
