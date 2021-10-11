from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta
import secrets
from place_model.place import Place
from website import modify_graph
import shortest_path

# http://127.0.0.1:5000
app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
app.permanent_session_lifetime = timedelta(days=5)


@app.before_request
def make_session_permanent():
    session.permanent = False


@app.route("/", methods=["POST", "GET"])
def home():
    if "location_name" not in session:
        session["location_name"] = []
        session["place_id"] = []
    return render_template("home.html", location_names=session["location_name"])


@app.route("/receiveDestination", methods=["POST"])
def receiveDestination():
    if request.method == "POST":
        place_details = request.get_json(force=True)
        process_place(modify_graph.create_place(place_details))
    return redirect(url_for("home"))

@app.route("/receiveHome", methods=["POST"])
def receiveHome():
    if request.method == "POST":
        place_details = request.get_json(force=True)
        process_place(modify_graph.create_home(place_details))
    return redirect(url_for("home"))


def process_place(new_place: Place):
    if new_place.place_id not in session["place_id"]:
        modify_graph.add_place(new_place)
        modify_graph.add_edges(new_place)

        session["place_id"].append(new_place.place_id)
        session["location_name"].append(new_place.name)
    print(session["location_name"])

def process_place_test(new_place: Place):
    modify_graph.add_place(new_place)
    modify_graph.add_edges(new_place)


if __name__ == "__main__":
    # app.run(debug=True)
    UCI_details = {'name': 'University of California Irvine', 'place_id': 'ChIJkb-SJQ7e3IAR7LfattDF-3k', 'formatted_address': 'Irvine, CA 92697, USA', 'type': ['university', 'point_of_interest', 'establishment'], 'business_status': 'OPERATIONAL'}
    Great_Park_details = {'name': 'Great Park Ice & Fivepoint Arena', 'place_id': 'ChIJgbGAbmLD3IARw5nd_Msw7RM', 'formatted_address': '888 Ridge Valley, Irvine, CA 92618, USA', 'type': ['point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 0, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 1, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 1, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 2, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 2, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 3, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 3, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 4, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 4, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 5, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 5, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 6, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 6, 'time': '0600', 'hours': 6, 'minutes': 0}}], 'weekday_text': ['Monday: 6:00 AM – 11:00 PM', 'Tuesday: 6:00 AM – 11:00 PM', 'Wednesday: 6:00 AM – 11:00 PM', 'Thursday: 6:00 AM – 11:00 PM', 'Friday: 6:00 AM – 11:00 PM', 'Saturday: 6:00 AM – 11:00 PM', 'Sunday: 6:00 AM – 11:00 PM']}, 'business_status': 'OPERATIONAL'}
    Spectrum_details = {'name': 'Irvine Spectrum Center', 'place_id': 'ChIJR892-fvn3IARQnnqgTu-Phc', 'formatted_address': '670 Spectrum Center Dr, Irvine, CA 92618, USA', 'type': ['shopping_mall', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 0, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 1, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 1, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 2, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 2, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 3, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 3, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 4, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 4, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 5, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 5, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 6, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 6, 'time': '1000', 'hours': 10, 'minutes': 0}}], 'weekday_text': ['Monday: 10:00 AM – 9:00 PM', 'Tuesday: 10:00 AM – 9:00 PM', 'Wednesday: 10:00 AM – 9:00 PM', 'Thursday: 10:00 AM – 9:00 PM', 'Friday: 10:00 AM – 10:00 PM', 'Saturday: 10:00 AM – 10:00 PM', 'Sunday: 10:00 AM – 9:00 PM']}, 'business_status': 'OPERATIONAL'}
    UCI = modify_graph.create_place(UCI_details)
    Great_Park = modify_graph.create_place(Great_Park_details)
    Spectrum = modify_graph.create_home(Spectrum_details)
    process_place_test(UCI)
    process_place_test(Great_Park)
    process_place_test(Spectrum)

    shortest_path.closest_neighbor(UCI)



