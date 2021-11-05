class Edge:
    def __init__(self, place1, place2, distance):
        self.place1 = place1
        self.place2 = place2
        self.distance = distance
        self.transport_time = {place1: None, place2: None}
        self.transport_mode = {place1: None, place2: None}

    def set_transport_time(self, destination, transport_time: int):
        self.transport_time[destination] = transport_time

    def get_transport_time(self, destination):
        return self.transport_time[destination]

    def set_transport_mode(self, destination, transport_mode: str):
        self.transport_mode[destination] = transport_mode

    def get_transport_mode(self, destination):
        return self.transport_mode[destination]

    def set_transport_info(self,destination, transport_time:int, transport_mode:str):
        self.set_transport_time(destination, transport_time)
        self.set_transport_mode(destination, transport_mode)

