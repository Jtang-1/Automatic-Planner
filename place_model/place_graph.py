from place_model.edge import Edge
from place_model.place import Place
from place_model.home import Home
import copy

import jsonpickle


class PlaceGraph:
    def __init__(self, vertex=None, edges=None):
        self.vertex, self.edges = set(), set()
        self._neighbors = {}
        if vertex:
            self.vertex = set(vertex)
            for v in self.vertex:
                self.add_vertex(v)
                self.check_if_home(v)
        if edges:
            self.edges = set(edges)
            for edge in self.edges:
                self.add_edge(edge)

    @property
    def num_edge(self):
        return len(self.edges)

    @property
    def num_vertices(self):
        return len(self._neighbors)

    @property
    def vertices(self):
        return self._neighbors.keys()

    @property
    def home(self):
        return self._home

    def degree(self, vertex: Place):
        return len(self._neighbors[vertex])

    def neighbors_edges(self, vertex: Place):
        return iter(self._neighbors[vertex])

    def add_vertex(self, vertex: Place):
        if vertex not in self._neighbors:
            self._neighbors[vertex] = set()
            self.check_if_home(vertex)

    def add_edge(self, edge: Edge):
        self.edges.add(edge)
        self.add_vertex(edge.place1)
        self.check_if_home(edge.place1)
        self.add_vertex(edge.place2)
        self.check_if_home(edge.place2)

        self._neighbors[edge.place1].add(edge)
        self._neighbors[edge.place2].add(edge)

    def remove_edge(self, edge: Edge):
        if edge in self.edges:
            self.edges.remove(edge)
            self._neighbors[edge.place1].remove(edge)
            self._neighbors[edge.place2].remove(edge)

    def get_edge(self, origin: Place, destination: Place):
        neighbors_edges = self.neighbors_edges(origin)
        for neighbor_edge in neighbors_edges:
            if neighbor_edge.place1 == destination or neighbor_edge.place2 == destination:
                return neighbor_edge

    def remove_vertex(self, vertex: Place):
        edges_to_delete = list(self.neighbors_edges(vertex))
        for e in edges_to_delete:
            self.remove_edge(e)
        del self._neighbors[vertex]

    def clear_graph(self):
        self.vertex, self.edges = set(), set()
        self._neighbors = {}

    def check_if_home(self, vertex):
        if isinstance(vertex, Home):
            self._home = vertex

if __name__ == "__main__":
    graph = PlaceGraph()
    place1 = Place("1", "mcdonald1")
    place2 = Place("2", "mcdonald2")
    place3 = Place("3", "mcdonald3")
    edge1 = Edge(place1, place2, 1)
    edge2 = Edge(place2, place3, 2)
    edge3 = Edge(place1, place3, 1)
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    graph.add_edge(edge3)
    for edge in graph.edges:
        print(edge.place1.name)  # prints mcdonald2, mcdonald1, mcdonald1
    print("just added edges")
    place4 = Place("4", "mcdonald4")
    graph.add_vertex(place4)
    print(graph.vertices)
    for place in graph.vertices:
        print(place.name)  # returns mcdonald...1,2,3, & 4
    print("just added place")

    graph.remove_edge(edge1)
    for edge in graph.edges:
        print(edge.place1.name)  # prints mcdonald2, mcdonald1
    for place in graph.vertices:
        print(place.name, "neighbors are")
        for neighbors in graph.neighbors_edges(place):
            if neighbors.place1 == place:
                print(neighbors.place2.name)
            else:
                print(neighbors.place1.name)  # returns mcdonald1(3),2(3),3(2,1),4(none)
    print("just removed edge1")

    graph.remove_vertex(place2)
    for edge in graph.edges:
        print(edge.place1.name)  # prints mcdonald1
    for place in graph.vertices:
        print(place.name, "neighbors are")
        for neighbors in graph.neighbors_edges(place):
            if neighbors.place1 == place:
                print(neighbors.place2.name)
            else:
                print(neighbors.place1.name)  # returns mcdonald1(3),3(1),4(none)
    print("just removed vertex place2")

    print("okay")
