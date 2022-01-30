const locations = document.querySelector("ol")


//Remove Place
addGlobalEventListener('click', "button", e => {
    const parent = e.target.parentNode
//    console.log("parent class name is", parent.className)
    if(parent.className === 'location_block'){
    locationNameElement = parent.querySelector(".locationName")
    locationName = locationNameElement.textContent
    place_id = locationNameElement.id
//    console.log("locationName is", locationName)
//    console.log("location PlaceID is", place_id)
    let placeIdJSON = JSON.stringify({
        "place_ID":place_id
        });
    var jsonResponse = sendInfo(placeIdJSON, "/removeLocation", removeMarker)
    const button = e.target
    const location = button.parentNode
    const locations = location.parentNode
        if(button.textContent === 'remove'){
            locations.removeChild(location)
        }
    }
});

//Show marker on map when location is clicked
addGlobalEventListener('click', ".locationName", e => {
//    console.log("clicked")
    locationNameElement = e.target
    locationName = locationNameElement.textContent
//    console.log("event listener for marker location name is", locationName)
    place_id = locationNameElement.id
    let placeIdJSON = JSON.stringify({
        "place_ID":place_id
    });
    sendInfo(placeIdJSON, "/getLocationIndex", displayMarkerContent);
});


function removeMarker(jsonResponse){
//    console.log('remove marker json response is', jsonResponse);
//    console.log('index to remove is', jsonResponse["index"]);
    index = jsonResponse["index"];
    markers[index].setMap(null);
    markers.splice(index, 1);
}

function displayMarkerContent(jsonResponse){
    index = jsonResponse["index"];
//    console.log("display marker index type is", typeof index)
    interested_marker = markers[index]
//    console.log("interseted marker content is", interested_marker.content)
//    console.log("content type is", typeof interested_marker.content)
    var infoWindow = new google.maps.InfoWindow({
                        content:interested_marker.getTitle()
                     });
    infoWindow.open(googleMapDisplayObject, interested_marker);

}

function sendPlaceInfo(place,url,callback){
        let location = JSON.stringify({
            "name":place.name,
            "place_id":place.place_id,
            "formatted_address":place.formatted_address,
            "type": place.types,
            "opening_hours":place.opening_hours,
            "business_status":place.business_status,
            "geometry":place.geometry
            });
        const request = new XMLHttpRequest();
        request.open("POST", url, true);
//        console.log("in sendPlaceInfo");
        request.onreadystatechange = () => {
            if (request.readyState==4){
//                console.log("SendPlaceInfo Loaded", request.response);
                if (typeof callback == 'function'){
                    callback();
//                    console.log("send Place info callback called");
                }
                $("#locations_block").load(" #locations_block > *");
            }
        };
        request.send(location);

}

function sendInfo(info, url, callback){
    const request = new XMLHttpRequest()
    request.open("POST", url, true)
    request.onreadystatechange = () => {
        if(request.readyState==4){
            var jsonResponse = JSON.parse(request.response)
//            console.log("SendInfo Loaded", jsonResponse);
            if (typeof callback == 'function'){
                callback(jsonResponse);
//                console.log("send info callback called")
            }
            $("#locations_block").load(" #locations_block > *");
//            console.log("after refresh",jsonResponse)
            return jsonResponse
        }
    };
//    console.log("time in sendInfo is", info)
//    console.log("type in send info is", typeof info)
    request.send(info)
}


function addGlobalEventListener(type, selector, callback){
    document.addEventListener(type, e=> {
        if (e.target.matches(selector)) callback(e)
    })
}

function hideVisitingAreaInput()
{
    localStorage.setItem('visiting_area_exists', 'True');
    setTimeout(function(){
        $("#visiting_area_display").load(" #visiting_area_display > *");
        document.getElementById("visiting_area_form").style.display="None";
        document.getElementById("visiting_area_display").style.display="block";
        document.getElementById("home_div").style.display="block";
        document.getElementById("destination_form").style.display="block";
        }, 700);
}

function showVisitingAreaInput()
{
    localStorage.removeItem('visiting_area_exists');
    document.getElementById("visiting_area_form").style.display="block";
    document.getElementById("visiting_area_display").style.display="None";
    document.getElementById("home_div").style.display="None";
    document.getElementById("destination_form").style.display="None";

}

function hideHomeInput()
{
    localStorage.setItem('home_exists', 'True');
    home_name = localStorage.getItem('home_name')
    setTimeout(function(){
        document.getElementById("home_form").style.display="None";
        document.getElementById("home_value_display").style.display="block";
        document.getElementById("home_name").textContent=home_name;
        }, 700);
}

function showHomeInput()
{
    localStorage.removeItem('home_exists');
    document.getElementById("home_form").style.display="block";
    document.getElementById("home_value_display").style.display="None";
    let placeIdJSON = JSON.stringify({
        "place_ID":""
    });
    var jsonResponse = sendInfo(placeIdJSON, "/removeHome", removeMarker)

}

//if visiting area exists
if (localStorage.getItem('visiting_area_exists')){
           document.getElementById("visiting_area_form").style.display="None";
           document.getElementById("visiting_area_display").style.display="block";
}

//if start date exists
if(localStorage.getItem('start_date')){
    date = localStorage.getItem('start_date')
    document.getElementById("start_date_input").value = reformatIsoDate(date);
    let start_date = JSON.stringify({
                    "start_date":date
                    });
   setTimeout(function(){
        sendInfo(start_date, "/receiveExistingStartDate")
        }, 500);
}

//if end date exists
if(localStorage.getItem('end_date')){
    date = localStorage.getItem('end_date')
    document.getElementById("end_date_input").value = reformatIsoDate(date);
    let end_date = JSON.stringify({
                    "end_date":date
                    });
    setTimeout(function(){
        sendInfo(end_date, "/receiveExistingEndDate")
        }, 1000);

}

//if home exists
if (localStorage.getItem('home_exists')){
    home_name = localStorage.getItem('home_name')
    document.getElementById("home_name").textContent=home_name;
    document.getElementById("home_form").style.display="None";
    document.getElementById("home_value_display").style.display="block";
}

//if leave time exists
if (localStorage.getItem('leave_time')){
    leave_time = localStorage.getItem("leave_time");
    document.getElementById("leave_time_input").value = leave_time;
//    console.log("in leave time exists value is", leave_time)
    let leave_time_json = JSON.stringify({
        "leave_time":leave_time
        });
    setTimeout(function(){
        sendInfo(leave_time_json, "/receiveExistingDayStartTime")
        }, 1500);
}

//if return time exists
if (localStorage.getItem('return_time')){
    return_time = localStorage.getItem("return_time");
    document.getElementById("return_time_input").value = return_time;
//    console.log("in return time exists value is", return_time)
    let return_time_json = JSON.stringify({
                    "return_time":return_time
                    });
    setTimeout(function(){
        sendInfo(return_time_json, "/receiveExistingDayEndTime");
        }, 2000);
}

function reformatIsoDate(date){
    date = date.split('-')
    year = date[0]
    month = date[1]
    day = date[2]
    return [month, day, year].join('-')
}

function removeAllDestinations(){
    sendInfo("", "/removeAllDestinations");
    if (localStorage.getItem('home_exists')){
        localStorage.removeItem('home_exists');
        document.getElementById("home_form").style.display="block";
        document.getElementById("home_value_display").style.display="None";
    }
    for (let i = 0; i<markers.length; i++){
        markers[i].setMap(null)
    }
    markers=[];

}

destination_form.addEventListener('submit', function(e){
//    console.log("in prevent default")
    e.preventDefault();
    sendDestination();
});

home_form.addEventListener('submit', function(e){
//    console.log("in prevent default")
    e.preventDefault();
});

visiting_area_form.addEventListener('submit', function(e){
//    console.log("in prevent default")
    e.preventDefault();
});

submitScheduleForm.addEventListener('submit', function(e){
    e.preventDefault();
    document.querySelectorAll("body :not(#loading)")
        .forEach(element => element.style.filter="blur(1px)");
    document.getElementById("loading").style.display="block";

    $.ajax({
        url:"/results",
        type: "POST",
        success: function(){
            location.href = 'results';
        },
        error: function(xhr, status, error){
            alert("All fields aren't filled out or departure time is in the past (choose a later start time or date)")
            document.getElementById("loading").style.display="none";
            document.querySelectorAll("body :not(#loading)")
                .forEach(element => element.style.filter="blur(0px)");
        }
    });
});

function loadScreen(){
    document.getElementById("loading").style.display = "block";
}