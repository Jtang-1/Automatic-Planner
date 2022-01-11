const locations = document.querySelector("ol")


//Remove Place
addGlobalEventListener('click', "button", e => {
    const parent = e.target.parentNode
    console.log("parent id is", parent.id)
    if(parent.className === 'location'){
    locationNameElement = parent.querySelector(".locationName")
    locationName = locationNameElement.textContent
    place_id = locationNameElement.id
    console.log("locationName is", locationName)
    console.log("location PlaceID is", place_id)
    let placeIdJSON = JSON.stringify({
        "place_ID":place_id
        });
    sendInfo(placeIdJSON, "/removeLocation")
    const button = e.target
    const location = button.parentNode
    const locations = location.parentNode
        if(button.textContent === 'remove'){
            locations.removeChild(location)
        }
    }
})


function sendInfo(info, url){
    const request = new XMLHttpRequest()
    request.open("POST", url, true)
    console.log("time in sendInfo is", info)
    console.log("type in send info is", typeof info)
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
        initMap();
        }, 700);

//        NEED TO FIGURE OUT HOW TO RELOAD VISITING AREA GEOMETRY DATA TO INIT MAP WITHOUT RELOADING PAGE
//        USE AJAX

}

function showVisitingAreaInput()
{
    localStorage.removeItem('visiting_area_exists');
    document.getElementById("visiting_area_form").style.display="block";
    document.getElementById("visiting_area_display").style.display="None";

}

//Hide Visiting Area if already selected
if (localStorage.getItem('visiting_area_exists')){
    hideVisitingAreaInput()
}

//If start date exists
if(localStorage.getItem('start_date')){
    document.getElementById("start_date").value = localStorage.getItem('start_date');
}

//If end date exists
if(localStorage.getItem('end_date')){
    document.getElementById("end_date").value = localStorage.getItem('end_date');
}
