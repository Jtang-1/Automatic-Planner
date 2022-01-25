addGlobalEventListener('click', "button", e => {
    locationNameElement = e.target
    buttoncontent = locationNameElement.textContent
    number = locationNameElement.id
    console.log("locationName is", buttoncontent)
    console.log("location PlaceID is", number)
    console.log("location number type is",typeof number)
    console.log("converted", Number(number))
    console.log('number value after converted is',typeof Number(number))

});

hide.addEventListener('click', function(e){
    console.log("marker hid")
    markers[0][0].setMap(null)
});

show.addEventListener('click', function(e){
    console.log("marker hid")
    markers[0][0].setMap(googleMapDisplayObject)
});

function addGlobalEventListener(type, selector, callback){
    document.addEventListener(type, e=> {
        if (e.target.matches(selector)) callback(e)
    })
}

var mapControlButtonElements = document.getElementsByClassName("mapControlButton");
console.log("class button elements", mapControlButtonElements)
for (var i=0; i<mapControlButtonElements.length; i++){
    mapControlButtonElements[i].textContent="Mark on map";
    mapControlButtonElements[i].addEventListener("click",e => {
        dayNum = e.target.id
        elementContent = e.target.textContent
        if (elementContent == "Minimize markers"){
            e.target.textContent="Mark on map"
        }
        else if(elementContent =="Mark on map"){
            e.target.textContent="Minimize markers"
        }
    });
};