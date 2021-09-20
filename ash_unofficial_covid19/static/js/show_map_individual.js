document.addEventListener("DOMContentLoaded", function() {
  var map = L.map('mapid', { "tap": false });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  var locationData = {}
  var latitude = JSON.parse(
    document.getElementById("results").dataset.latitude);
  var longitude = JSON.parse(
    document.getElementById("results").dataset.longitude);
  var locationName = JSON.parse(JSON.stringify(
    document.getElementById("results").dataset.name));
  locationData["latitude"] = latitude
  locationData["longitude"] = longitude
  locationData["locationName"] = locationName

  map.setView([locationData["latitude"], locationData["longitude"]], 17);

  L.marker([
    locationData["latitude"],
    locationData["longitude"]
  ], { icon: L.divIcon({
          html: "<i class='fas fa-clinic-medical fa-3x'></i>",
          className: "map_icon",
          iconSize: [0, 0]
      })
    }).addTo(map)
    .bindPopup(locationData["locationName"], {autoClose:
      false})
    .openPopup();

}, false);
