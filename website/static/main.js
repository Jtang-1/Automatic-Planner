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
        }, 700);
}

function showVisitingAreaInput()
{
    localStorage.removeItem('visiting_area_exists');
    document.getElementById("visiting_area_form").style.display="block";
    document.getElementById("visiting_area_display").style.display="None";

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
}

//if end date exists
if(localStorage.getItem('end_date')){
    date = localStorage.getItem('end_date')
    document.getElementById("end_date_input").value = reformatIsoDate(date);
}

//if home exists
if (localStorage.getItem('home_exists')){
    home_name = localStorage.getItem('home_name')
    document.getElementById("home_name").textContent=home_name;
    document.getElementById("home_form").style.display="None";
    document.getElementById("home_value_display").style.display="block";
}


function reformatIsoDate(date){
    date = date.split('-')
    year = date[0]
    month = date[1]
    day = date[2]
    return [month, day, year].join('-')
}