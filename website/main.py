from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta
from website.website_helpers import *
import secrets
from place_model.edge import Edge
from place_model.place import Place
from place_model.place_graph import PlaceGraph
import place_model.google_map_distance_matrix as dist_api

import copy
# http://127.0.0.1:5000
app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
app.permanent_session_lifetime = timedelta(days=5)

graph = PlaceGraph()

@app.before_request
def make_session_permanent():
    session.permanent = False


@app.route("/", methods=["POST", "GET"])
def home():
    if "location_name" not in session:
        session["location_name"] = []
        session["place_id"] = []
    return render_template("home.html", location_names=session["location_name"])


@app.route("/processLocation", methods=["POST"])
def processLocation():
    if request.method == "POST":
        place_details = request.get_json(force=True)
        if place_details["place_id"] not in session["place_id"]:
            new_place = create_place(place_details)
            add_place(new_place)
            add_edges(new_place)
        print(session["location_name"])
        return redirect(url_for("home"))
    return render_template("home.html", location_names=session["location_name"])


def create_place(place_details):
    place_type = key_value("type", place_details)
    opening_hours = key_value("opening_hours", place_details)
    business_status = key_value("business_status", place_details)
    return Place(place_details["place_id"], place_details["name"], place_type,
                 opening_hours, business_status)


def add_place(new_place: Place):
    session["place_id"].append(new_place.place_id)
    session["location_name"].append(new_place.name)
    graph.add_vertex(new_place)
    # for v in graph.vertices:
    #     if new_place == v:
    #         print("True")


def add_edges(new_place: Place) -> Edge:
    distance_dict = neighboring_distances(new_place)
    print("distance dict in add_edges is", distance_dict)
    for place in graph.vertices:
        if place != new_place:
            print("new_place is", new_place)
            print("place in add_edges is", place)
            dist_to_neighbor = distance_dict[new_place][place]
            graph.add_edge(Edge(place, new_place, dist_to_neighbor))
    print(graph.num_edge)


def remove_place(place_details):
    pass


def neighboring_distances(place: Place) -> dict[Place, dict[Place, int]]:
    existing_places = set(graph.vertices)
    print("Existing_places are", existing_places)
    print("passed in place is", place)
    existing_places.remove(place)
    if len(existing_places) != 0:
        distance_dict = dist_api.distance_dict(place, list(existing_places))
        print("this is distance_dict", distance_dict)
        print("this is disntace_shllow copy", copy.copy(distance_dict))
        return distance_dict



def create_edges(place: Place):
    pass


if __name__ == "__main__":
    app.run(debug=True)
