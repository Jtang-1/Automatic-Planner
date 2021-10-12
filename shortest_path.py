from website import modify_graph
from place_model.place import Place
from place_model.home import Home
from day_itinerary import DayItinerary
import copy

graph = modify_graph.get_graph()
graph_copy = copy.copy(graph)


def create_day_itinerary():
    home = graph.home
    print("home is", home.name)
    farthest_neighbor = farthest_not_home_neighbor(home)
    print("farthest neighbor is", farthest_neighbor.name)
    visit_order = [home, farthest_neighbor]

    visit_order = visit_order + shortest_route_from(farthest_neighbor)
    print([(count, place.name) for count, place in enumerate(visit_order)])
    return visit_order


def shortest_route_from(node: Place) -> []:
    total_path_connections = graph_copy.num_vertices - 2
    visit_order = []
    current_place = node
    for _ in range(total_path_connections):
        print("in for loop")
        next_place = closest_not_home_neighbor(current_place)
        graph_copy.remove_vertex(current_place)
        visit_order.append(next_place)
        current_place = next_place
    # for count, place in enumerate(visit_order):
    #     print(count, place.name)
    return visit_order


def closest_not_home_neighbor(node: Place) -> Place:
    print("vertices of copies", list(graph_copy.vertices))
    print("passed in node", node.name)
    neighbors_edges = graph_copy.neighbors_edges(node)
    closest_neighbor_dist = float('inf')
    closest_neighbor = None
    for edge in neighbors_edges:
        if edge.distance > closest_neighbor_dist:
            continue
        if edge.place1 != node and not isinstance(edge.place1, Home):
            closest_neighbor = edge.place1
        elif edge.place2 != node and not isinstance(edge.place2, Home):
            closest_neighbor = edge.place2
        else:
            continue
        closest_neighbor_dist = edge.distance

    print("closest neighbor", closest_neighbor.name,  closest_neighbor_dist)
    return closest_neighbor


def farthest_not_home_neighbor(node: Place) -> Place:
    neighbors_edges = graph_copy.neighbors_edges(node)
    farthest_neighbor_dist = 0
    farthest_neighbor = None
    for edge in neighbors_edges:
        if edge.distance < farthest_neighbor_dist:
            continue
        if edge.place1 != node and not isinstance(edge.place1, Home):
            farthest_neighbor = edge.place1
        elif edge.place2 != node and not isinstance(edge.place2, Home):
            farthest_neighbor = edge.place2
        else:
            continue
        farthest_neighbor_dist = edge.distance

    print("farthest neighbor", farthest_neighbor.name, farthest_neighbor_dist)
    return farthest_neighbor
