import json
import jsonpickle


class PlaceGraph():
    def __init__(self, vertex=None, edges=None):
        self.vertex, self.edges = set(), set(frozenset())
        self._neighbors = {}
        if vertex is not None:
            self.vertex = set(vertex)
            for v in self.vertex:
                self.add_vertex(v)
        if edges is not None:
            self.edges = set(frozenset((u, v)) for u, v in edges)
            for u, v, in self.edges:
                self.add_edge(u, v)

    def to_json(self):
        self._neighbors = jsonpickle.encode(self._neighbors, keys=True)
        return jsonpickle.encode(self, keys=True)

    def to_obj(self):
        self._neighbors = jsonpickle.decode(self._neighbors, keys=True)

    @property
    def vertices(self):
        return self._neighbors.keys()

    def degree(self, vertex):
        return len(self._neighbors(vertex))

    def neighbors(self, vertex):
        return iter(self._neighbors[vertex])

    def add_vertex(self, vertex):
        if vertex not in self._neighbors:
            self._neighbors[vertex] = set()

    def add_edge(self, u, v):
        self.edges.add(frozenset((u, v)))
        self.add_vertex(u)
        self.add_vertex(v)
        self._neighbors[u].add(v)
        self._neighbors[v].add(u)

    @property
    def num_edge(self):
        return len(self.edges)

    @property
    def num_vertices(self):
        return len(self._neighbors)

    def remove_edge(self, u, v):
        e = frozenset((u, v))
        if e in self.edges:
            self.edges.remove(frozenset((u, v)))
            self._neighbors[u].remove(v)
            self._neighbors[v].remove(u)

    def remove_vertex(self, u):
        to_delete = list(self.neighbors(u))
        for v in to_delete:
            self.remove_edge(u, v)
        del self._neighbors[u]


if __name__ == "__main__":
    G1 = PlaceGraph([1, 2, 3], {(1, 2), (2, 3)})
    G2 = PlaceGraph()
    G1.add_edge(3,2)
    G2.add_edge(4,1)
    G2.add_edge(3,1)
    G1.add_vertex(5)
    G2.add_vertex(5)
    G1.add_vertex(2)
    G2.add_vertex(2)
    print(list(G1._neighbors.keys()))
    print(list(G2.neighbors(3)))
    print("edges are", G1.edges)
    G1.remove_edge(1, 2)
    print(G1.vertices)
    G1.remove_vertex(1)
    print(G1.vertices)
    for x in G1.vertices:
        print(x)
    print("okay")
