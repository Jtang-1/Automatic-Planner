from website import modify_graph
from place_model.place import Place
import copy

graph = modify_graph.get_graph()
graph_copy = copy.copy(graph)

def find_shortest_path() -> []:
    home = graph.home
    total_path_connections = graph_copy.num_vertices - 1
    visit_order = [home]
    current_place = home
    for _ in range(total_path_connections):
        print("in for loop")
        next_place = find_closest_neighbor(current_place)
        graph_copy.remove_vertex(current_place)
        visit_order.append(next_place)
        current_place = next_place
    for count, place in enumerate(visit_order):
        print(count, place.name)
    return visit_order


def find_closest_neighbor(node: Place) -> Place:
    print("vertices of copies", list(graph_copy.vertices))
    print("passed in node", node)
    neighbors_edges = graph_copy.neighbors_edges(node)
    closest_neighbor_dist = float('inf')
    closest_neighbor = None
    for edge in neighbors_edges:
        if edge.distance > closest_neighbor_dist:
            continue
        closest_neighbor_dist = edge.distance
        if edge.place1 != node:
            closest_neighbor = edge.place1
        else:
            closest_neighbor = edge.place2
    print(edge.place2.name, edge.distance)
    print(edge.place1.name, edge.distance)
    return closest_neighbor
