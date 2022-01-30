# Automatic-Planner

Automatic Planner is an idea I created to automate the hardest part of vacation planning. This is a webpage run through Flask that utilizes
data from Google Map API to generate the most optimized route for each day of the trip.

It is currently deployed on https://automaticplanner.herokuapp.com

How it works:
The user inputs general information about their trip: 
1. The area that they are visiting
2. Vacation Dates
3. The timne they would like to start and end their day
4. Where they are staying
5. Where they want to visit

Google Map API autocompletes location by prioritizing places in the area being visited. Place details data on the places such as visiting hours and
location. The information is passed back and forth between front and back end via AJAX, Flask, and Redis is used to store server-side session data.
On the backend, I used a graph to organize the data and created an algorithm to generate the optimized route for each day of the trip. 
