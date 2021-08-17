document.addEventListener("DOMContentLoaded", function() {
    var resultsLength = Number(JSON.parse(
        document.getElementById("results").dataset.length));

    var map = L.map('mapid');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var locationData = {}
    for (var i = 0; i < resultsLength; i++) {
        var currentOrder = String(i + 1)
        var latitude = JSON.parse(
            document.getElementById("order" + currentOrder).dataset.latitude);
        var longitude = JSON.parse(
            document.getElementById("order" + currentOrder).dataset.longitude);
        var locationName = JSON.parse(JSON.stringify(
            document.getElementById("order" + currentOrder).dataset.name));
        locationData["latitude" + currentOrder] = latitude
        locationData["longitude" + currentOrder] = longitude
        locationData["locationName" + currentOrder] = locationName
    }

    // 中心地を1番目の検索結果の場所にセットする
    map.setView([locationData["latitude" + "1"], locationData["longitude" + "1"]], 14);

    for (var i = 0; i < resultsLength; i++) {
        var currentReversedOrder = String(resultsLength - i)
        L.marker([
            locationData["latitude" + currentReversedOrder],
            locationData["longitude" + currentReversedOrder]
        ]).addTo(map)
            .bindPopup(locationData["locationName" + currentReversedOrder])
            .openPopup();
    }

}, false);
