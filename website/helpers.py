import jsonpickle


def key_value(key, dictionary):
    if key in dictionary:
        return dictionary[key]
    else:
        return None


def decode_graph(encoded_graph):
    graph = jsonpickle.decode(encoded_graph)
    graph.to_obj()
    return graph