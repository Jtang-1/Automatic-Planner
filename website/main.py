from flask import Flask, render_template, request, session, redirect, url_for, g
from datetime import timedelta
from helpers import *
import secrets
from place.place_graph import *
from place.place import *

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
app.permanent_session_lifetime = timedelta(days=5)


@app.before_first_request
def initiate():
    session["graph"] = PlaceGraph().to_json()


@app.before_request
def make_session_permanent():
    session.permanent = False


@app.route("/", methods=["POST", "GET"])
def home():
    if "location" not in session:
        session["location"] = []
        session["place_id"] = []
    return render_template("home.html", locations=session["location"])


@app.route("/processLocation", methods=["POST"])
def processLocation():
    if request.method == "POST":
        place_details = request.get_json(force=True)
        if place_details["place_id"] not in session["place_id"]:
            add_place(place_details)
        print(session["location"])
        return redirect(url_for("home"))
    return render_template("home.html", locations=session["location"])


def create_place(place_details):
    place_type = key_value("type", place_details)
    opening_hours = key_value("opening_hours", place_details)
    business_status = key_value("business_status", place_details)
    return Place(place_details["place_id"], place_details["name"], place_type,
                 opening_hours, business_status)


def add_place(place_details):
    session["place_id"].append(place_details["place_id"])
    session["location"].append(place_details["name"])

    new_place = create_place(place_details)
    graph = decode_graph(session["graph"])
    graph.add_vertex(new_place)
    session["graph"] = graph.to_json()


def remove_place(place_details):
    pass


if __name__ == "__main__":
    app.run(debug=True)
