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


@app.route("/results", methods=["GET"])
def results():
    ordered_locations = shortest_path.create_day_itinerary()
    ordered_named_locations = [place.name for place in ordered_locations]
    return render_template("results.html", ordered_locations=ordered_named_locations)


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
     app.run(debug=True)
    # UCI_details = {'name': 'University of California Irvine', 'place_id': 'ChIJkb-SJQ7e3IAR7LfattDF-3k', 'formatted_address': 'Irvine, CA 92697, USA', 'type': ['university', 'point_of_interest', 'establishment'], 'business_status': 'OPERATIONAL'}
    # Great_Park_details = {'name': 'Great Park Ice & Fivepoint Arena', 'place_id': 'ChIJgbGAbmLD3IARw5nd_Msw7RM', 'formatted_address': '888 Ridge Valley, Irvine, CA 92618, USA', 'type': ['point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 0, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 1, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 1, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 2, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 2, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 3, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 3, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 4, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 4, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 5, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 5, 'time': '0600', 'hours': 6, 'minutes': 0}}, {'close': {'day': 6, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 6, 'time': '0600', 'hours': 6, 'minutes': 0}}], 'weekday_text': ['Monday: 6:00 AM – 11:00 PM', 'Tuesday: 6:00 AM – 11:00 PM', 'Wednesday: 6:00 AM – 11:00 PM', 'Thursday: 6:00 AM – 11:00 PM', 'Friday: 6:00 AM – 11:00 PM', 'Saturday: 6:00 AM – 11:00 PM', 'Sunday: 6:00 AM – 11:00 PM']}, 'business_status': 'OPERATIONAL'}
    # Spectrum_details = {'name': 'Irvine Spectrum Center', 'place_id': 'ChIJR892-fvn3IARQnnqgTu-Phc', 'formatted_address': '670 Spectrum Center Dr, Irvine, CA 92618, USA', 'type': ['shopping_mall', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 0, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 1, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 1, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 2, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 2, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 3, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 3, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 4, 'time': '2100', 'hours': 21, 'minutes': 0}, 'open': {'day': 4, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 5, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 5, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 6, 'time': '2200', 'hours': 22, 'minutes': 0}, 'open': {'day': 6, 'time': '1000', 'hours': 10, 'minutes': 0}}], 'weekday_text': ['Monday: 10:00 AM – 9:00 PM', 'Tuesday: 10:00 AM – 9:00 PM', 'Wednesday: 10:00 AM – 9:00 PM', 'Thursday: 10:00 AM – 9:00 PM', 'Friday: 10:00 AM – 10:00 PM', 'Saturday: 10:00 AM – 10:00 PM', 'Sunday: 10:00 AM – 9:00 PM']}, 'business_status': 'OPERATIONAL'}
    # Disneyland_details= {'name': 'Disneyland Park', 'place_id': 'ChIJa147K9HX3IAR-lwiGIQv9i4', 'formatted_address': '1313 Disneyland Dr, Anaheim, CA 92802, USA', 'type': ['tourist_attraction', 'amusement_park', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 0, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 1, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 1, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 2, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 2, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 3, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 3, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 4, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 4, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 5, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 5, 'time': '0800', 'hours': 8, 'minutes': 0}}, {'close': {'day': 6, 'time': '2300', 'hours': 23, 'minutes': 0}, 'open': {'day': 6, 'time': '0800', 'hours': 8, 'minutes': 0}}], 'weekday_text': ['Monday: 8:00 AM – 11:00 PM', 'Tuesday: 8:00 AM – 11:00 PM', 'Wednesday: 8:00 AM – 11:00 PM', 'Thursday: 8:00 AM – 11:00 PM', 'Friday: 8:00 AM – 11:00 PM', 'Saturday: 8:00 AM – 11:00 PM', 'Sunday: 8:00 AM – 11:00 PM']}, 'business_status': 'OPERATIONAL'}
    # Southcoast_details = {'name': 'South Coast Plaza', 'place_id': 'ChIJCyDHJSXf3IAR2DBM02jy2dE', 'formatted_address': '3333 Bristol St, Costa Mesa, CA 92626, USA', 'type': ['shopping_mall', 'point_of_interest', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '1900', 'hours': 19, 'minutes': 0}, 'open': {'day': 0, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 1, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 1, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 2, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 2, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 3, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 3, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 4, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 4, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 5, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 5, 'time': '1100', 'hours': 11, 'minutes': 0}}, {'close': {'day': 6, 'time': '2000', 'hours': 20, 'minutes': 0}, 'open': {'day': 6, 'time': '1100', 'hours': 11, 'minutes': 0}}], 'weekday_text': ['Monday: 11:00 AM – 8:00 PM', 'Tuesday: 11:00 AM – 8:00 PM', 'Wednesday: 11:00 AM – 8:00 PM', 'Thursday: 11:00 AM – 8:00 PM', 'Friday: 11:00 AM – 8:00 PM', 'Saturday: 11:00 AM – 8:00 PM', 'Sunday: 11:00 AM – 7:00 PM']}, 'business_status': 'OPERATIONAL'}
    # Costco_details =  {'name': 'Costco Wholesale', 'place_id': 'ChIJYa9Pxlbd3IARpbubX7xROaQ', 'formatted_address': '115 Technology Dr, Irvine, CA 92618, USA', 'type': ['department_store', 'point_of_interest', 'store', 'establishment'], 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '1800', 'hours': 18, 'minutes': 0}, 'open': {'day': 0, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 1, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 1, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 2, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 2, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 3, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 3, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 4, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 4, 'time': '0900', 'hours': 9, 'minutes': 0}}, {'close': {'day': 5, 'time': '2030', 'hours': 20, 'minutes': 30}, 'open': {'day': 5, 'time': '1000', 'hours': 10, 'minutes': 0}}, {'close': {'day': 6, 'time': '1800', 'hours': 18, 'minutes': 0}, 'open': {'day': 6, 'time': '0930', 'hours': 9, 'minutes': 30}}], 'weekday_text': ['Monday: 10:00 AM – 8:30 PM', 'Tuesday: 9:00 AM – 8:30 PM', 'Wednesday: 10:00 AM – 8:30 PM', 'Thursday: 9:00 AM – 8:30 PM', 'Friday: 10:00 AM – 8:30 PM', 'Saturday: 9:30 AM – 6:00 PM', 'Sunday: 10:00 AM – 6:00 PM']}, 'business_status': 'OPERATIONAL'}
    #
    #
    # UCI = modify_graph.create_place(UCI_details)
    # Great_Park = modify_graph.create_place(Great_Park_details)
    # Spectrum = modify_graph.create_home(Spectrum_details)
    # Disneyland = modify_graph.create_place(Disneyland_details)
    # Southcoast = modify_graph.create_place(Southcoast_details)
    # Costco = modify_graph.create_place(Costco_details)
    #
    # process_place_test(UCI)
    # process_place_test(Great_Park)
    # process_place_test(Spectrum)
    # process_place_test(Disneyland)
    # process_place_test(Southcoast)
    # process_place_test(Costco)
    #
    # shortest_path.create_day_itinerary()
