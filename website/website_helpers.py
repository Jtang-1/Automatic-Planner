import jsonpickle


def key_value(key, dictionary):
    if key in dictionary:
        return dictionary[key]
    else:
        return None
