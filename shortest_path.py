from website import modify_graph
from place_model.place import Place

graph = modify_graph.get_graph()


def closest_neighbor(node: Place) -> Place:
    neighbors_edges = graph.neighbors_edges(node)
    closest_neighbor_dist = float('inf')
    for edge in neighbors_edges:
        if edge.place1.name == node.name:
            print(edge.place2.name, edge.distance)
        else:
            print(edge.place1.name, edge.distance)