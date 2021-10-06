import requests
import time
import urllib.error
from urllib.parse import urlencode


def create_encoded_url(parameters: dict, endpoint: str) -> str:
    url_parameters = urlencode(parameters)
    return f"{endpoint}?{url_parameters}"


def get_url_response(url: str) -> dict:
    current_delay = 0.1
    max_delay = 5
    while True:
        try:
            response = requests.get(url)
        except urllib.error.URLError:
            pass
        else:
            result = response.json()
            if result["status"] == "OK":
                return response.json()
            elif result["status"] !="UNKNOWN_ERROR":
                raise Exception(result["error_message"])

        if current_delay > max_delay:
            raise Exception("Too many retry attempts.")
        print("Waiting", current_delay, "seconds before retrying")
        time.sleep(current_delay)
        current_delay *= 2