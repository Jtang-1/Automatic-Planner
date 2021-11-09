class Edge:
    def __init__(self, place1, place2, distance):
        self.place1 = place1
        self.place2 = place2
        self.distance = distance
        self.transport_time_to = {place1: None, place2: None}
        self.transport_mode_to = {place1: None, place2: None}

    def set_time_transport_to(self, destination, transport_time: int):
        self.transport_time_to[destination] = transport_time

    def get_time_transport_to(self, destination):
        return self.transport_time_to[destination]

    def set_mode_transport_to(self, destination, transport_mode: str):
        self.transport_mode_to[destination] = transport_mode

    def get_mode_transport_to(self, destination):
        return self.transport_mode_to[destination]

    def set_info_transport_to(self, destination, transport_time: int, transport_mode: str):
        self.set_time_transport_to(destination, transport_time)
        self.set_mode_transport_to(destination, transport_mode)

    def is_edge_for(self, place1, place2):
        print("place1 is", place1)
        print("place2 is", place2)
        print("self.place1 is", self.place1)
        print("self.place2 is", self.place2)
        if self.place1 == place1 or self.place1 == place2:
            if self.place2 == place1 or self.place2 == place2:
                return True
        return False
