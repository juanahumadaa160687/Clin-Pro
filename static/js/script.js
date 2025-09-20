function iniciarMap(){
    const coord = {lat: -20.241004, lng: -70.144530};
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: coord
    });
    const marker = new google.maps.Marker({
        position: coord,
        map: map
    });
}

