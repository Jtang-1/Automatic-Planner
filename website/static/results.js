var numberedIcon = "http://maps.google.com/mapfiles/kml/paddle/"

function addGlobalEventListener(type, selector, callback){
    document.addEventListener(type, e=> {
        if (e.target.matches(selector)) callback(e)
    })
}

var mapControlButtonElements = document.getElementsByClassName("mapControlButton");
//console.log("class button elements", mapControlButtonElements)
for (var i=0; i<mapControlButtonElements.length; i++){
    mapControlButtonElements[i].textContent="Mark on map";
    mapControlButtonElements[i].addEventListener("click",e => {
        dayNum = Number(e.target.id)
        elementContent = e.target.textContent
        //actions associated with minimizing markers
        if (elementContent == "Minimize markers"){
            unmarkOnMapDayPlan(dayNum);
//            console.log("1previous sibling is", e.target.previousSibling)
            e.target.previousSibling.style.borderColor = "#A41623"
            e.target.textContent="Mark on map"
        }
        //actions associated with marking markers
        else if(elementContent =="Mark on map"){
            markOnMapDayPlan(dayNum);
//            console.log("2previous sibling is", e.target.previousSibling)
            e.target.previousSibling.style.borderColor = "#3ABEFF"
            e.target.textContent="Minimize markers"
        }
    });
};

//change Markers in day to numbered
function markOnMapDayPlan(dayNum){
    dayDestinationMarkers = markers[dayNum]
    for (var i=0; i<dayDestinationMarkers.length; i++){
        icon_num = i+2
        if (icon_num <= 10) {
            icon = {url:numberedIcon + String(icon_num) + ".png", scaledSize: new google.maps.Size(50,50)}
            dayDestinationMarkers[i].setIcon(icon)
        }
        else if (icon_num <= 25){
            letter = String.fromCharCode(65 - 11 + icon_num);
//            console.log("letter is", letter)
            icon = {url:numberedIcon+letter+".png", scaledSize: new google.maps.Size(50,50)}
            dayDestinationMarkers[i].setIcon(icon)
        }
        else{
            dayDestinationMarkers[i].setIcon(icon)
        }
    }
}

//change Markers in day to default
function unmarkOnMapDayPlan(dayNum){
    dayDestinationMarkers = markers[dayNum]
    for (var i=0; i<dayDestinationMarkers.length; i++){
        dayDestinationMarkers[i].setIcon()
    }
}