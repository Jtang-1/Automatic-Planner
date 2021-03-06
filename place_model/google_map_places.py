from helpers import *
# import config
import os

import requests

api_key = os.environ["AUTOMATIC_PLANNER_GOOGLE_API_KEY"]
data_type = 'json'
language = "en"
fields = "name,formatted_address,type,opening_hours,business_status"


def get_place_id(address: str) -> str:
    place_search_endpoint = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/{data_type}'
    parameters = {"input": address, "inputtype": "textquery", "fields": "place_id",
                  "language": language, "key": api_key}
    url = create_encoded_url(parameters, place_search_endpoint)
    return get_url_response(url)["candidates"][0]["place_id"]


#returns api json response as dict
def place_details(address: str) -> dict:
    place_id = get_place_id(address)
    place_details_endpoint = f'https://maps.googleapis.com/maps/api/place/details/{data_type}'
    parameters = {"place_id": place_id, "fields": fields,
                  "language": language, "key": api_key}
    url = create_encoded_url(parameters, place_details_endpoint)
    return get_url_response(url)

