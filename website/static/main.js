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
//addGlobalEventListener("click", "button", e => {
//    console.log("hi")
//    alert("hi")
//
//})

function addGlobalEventListener(type, selector, callback){
    document.addEventListener(type, e=> {
        if (e.target.matches(selector)) callback(e)
    })
}
