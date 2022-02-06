document.addEventListener("DOMContentLoaded", function() {
  var resultsLength = Number(JSON.parse(
    document.getElementById("results").dataset.length));

  var map = L.map('mapid', { "tap": false });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  var locationData = {}
  var latitudeSum = 0
  var longitudeSum = 0
  for (var i = 0; i < resultsLength; i++) {
    var currentOrder = String(i + 1)
    var latitude = JSON.parse(
      document.getElementById("order" + currentOrder).dataset.latitude);
    var longitude = JSON.parse(
      document.getElementById("order" + currentOrder).dataset.longitude);
    var locationName = JSON.parse(JSON.stringify(
      document.getElementById("order" + currentOrder).dataset.name));
    var url = JSON.parse(JSON.stringify(
      document.getElementById("order" + currentOrder).dataset.url));
    locationData["latitude" + currentOrder] = latitude
    locationData["longitude" + currentOrder] = longitude
    var parentPath = ""
    if (document.getElementById("firstReservationStatus")) {
      parentPath = "first_reservation_status"
    } else {
      parentPath = "reservation_status"
    }
    locationData["locationName" + currentOrder] = "<a href='/" + parentPath + "/medical_institution/" + url + "'>" + locationName + "</a>"
    latitudeSum += latitude
    longitudeSum += longitude
  }
  if (resultsLength == 0) {
    locationData["centerLatitude"] = 43.77075624195208
    locationData["centerLongitude"] = 142.36518924439247
  } else {
    locationData["centerLatitude"] = latitudeSum / resultsLength
    locationData["centerLongitude"] = longitudeSum / resultsLength
  }

  var zoomLevel = 0
  if (document.getElementById("areaMap")) {
    zoomLevel = 15
  } else if (document.getElementById("medicalInstitutionMap")) {
    zoomLevel = 16
  } else {
    zoomLevel = 14
  }
  map.setView([locationData["centerLatitude"], locationData["centerLongitude"]], zoomLevel);

  for (var i = 0; i < resultsLength; i++) {
    var currentReversedOrder = String(resultsLength - i)
    var marker = L.marker([
        locationData["latitude" + currentReversedOrder],
        locationData["longitude" + currentReversedOrder]
      ])
    if (document.getElementById("allMap")) {
      marker.addTo(map)
        .bindPopup(locationData["locationName" + currentReversedOrder], {autoClose:
          false});
    } else {
      marker.addTo(map)
        .bindPopup(locationData["locationName" + currentReversedOrder], {autoClose:
          false})
        .openPopup();
    }
  }
}, false);
