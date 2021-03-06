import jsonpickle
import datetime


def key_value(key, dictionary):
    if key in dictionary:
        return dictionary[key]
    else:
        return None


def time_to_minutesdelta(time: datetime.time) -> datetime.timedelta:
    minute = time.hour * 60 + time.minute + time.second / 60
    minutes_change = datetime.timedelta(minutes=minute)
    return minutes_change


# Yield successive n-sized chunks from lst
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
