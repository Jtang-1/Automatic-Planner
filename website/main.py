from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta
from website.helpers import *
import secrets
from place_model.edge import Edge
from place_model.place import Place
from place_model.place_graph import PlaceGraph
import place_model.google_map_distance_matrix as dist_api
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
            # add_edges(new_place)
            # neighboring_distances(new_place)
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
    print(session["location_name"])
    graph.add_vertex(new_place)
    for v in graph.vertices:
        if new_place == v:
            print("True")

# def add_edges(new_place: Place):
#     graph = decode_graph(session["graph"])
#     for place in graph.vertices:
#         if place != new_place:
#             graph.add_edge(Edge(place, new_place))
#     print(graph.num_edge)
#     session["graph"] = graph.to_json()


def remove_place(place_details):
    pass


def neighboring_distances(place: Place):
    existing_places = graph.neighbors(place)
    existing_places.remove(place)
    print(list(existing_places))
    print("type", existing_places)
    distance_dict = dist_api.distance_dict(place, list(existing_places))
    print("this is distance_dict", distance_dict)




def create_edges(place: Place):
    pass


if __name__ == "__main__":
    app.run(debug=True)
