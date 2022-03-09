document.addEventListener(
  "DOMContentLoaded",
  function () {
    var resultsLength = Number(
      JSON.parse(document.getElementById("results").dataset.length)
    );

    var map = L.map("mapid", { tap: false });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    var locationDataList = {};
    var latitudeSum = 0;
    var longitudeSum = 0;
    for (var i = 0; i < resultsLength; i++) {
      var currentOrder = String(i + 1);
      var locationName = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.name
        )
      );
      var latitude = JSON.parse(
        document.getElementById("order" + currentOrder).dataset.latitude
      );
      var longitude = JSON.parse(
        document.getElementById("order" + currentOrder).dataset.longitude
      );
      var url = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.url
        )
      );
      var vaccine = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.vaccine
        )
      );
      var status = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.status
        )
      );
      var parentPath = "";
      if (document.getElementById("firstReservationStatus")) {
        parentPath = "first_reservation_status";
      } else if (document.getElementById("childReservationStatus")) {
        parentPath = "child_reservation_status";
      } else {
        parentPath = "reservation_status";
      }
      var nameLink =
        "<a href='/" +
        parentPath +
        "/medical_institution/" +
        url +
        "'>" +
        locationName +
        "</a>";
      if (locationDataList[locationName] === undefined) {
        if (vaccine === "") {
          status = "予約受付状況: " + status;
        } else {
          status = vaccine + "<br>" + "予約受付状況: " + status;
        }
      } else {
        if (vaccine === "") {
          status =
            locationDataList[locationName]["status"] +
            "<br>" +
            "予約受付状況: " +
            status;
        } else {
          status =
            locationDataList[locationName]["status"] +
            "<br>" +
            vaccine +
            "<br>" +
            "予約受付状況: " +
            status;
        }
      }
      locationDataList[locationName] = {
        locationName: locationName,
        latitude: latitude,
        longitude: longitude,
        nameLink: nameLink,
        status: status,
      };
      latitudeSum += latitude;
      longitudeSum += longitude;
    }

    var centerLatitude = 43.77075624195208;
    var centerLongitude = 142.36518924439247;
    if (0 < resultsLength) {
      centerLatitude = latitudeSum / resultsLength;
      centerLongitude = longitudeSum / resultsLength;
    }

    var zoomLevel = 0;
    if (document.getElementById("areaMap")) {
      zoomLevel = 15;
    } else if (document.getElementById("gpsMap")) {
      zoomLevel = 14;
    } else if (document.getElementById("medicalInstitutionMap")) {
      zoomLevel = 16;
    } else {
      if (document.getElementById("childReservationStatus")) {
        zoomLevel = 12;
      } else {
        zoomLevel = 14;
      }
    }

    if (document.getElementById("gpsMap")) {
      var currentLongitude = parseFloat(
        JSON.parse(document.getElementById("results").dataset.currentlongitude)
      );
      var currentLatitude = parseFloat(
        JSON.parse(document.getElementById("results").dataset.currentlatitude)
      );
      map.options.closePopupOnClick = false;
      map.setView([currentLatitude, currentLongitude], zoomLevel);
      var currentPointMarker = L.marker([currentLatitude, currentLongitude]);
      currentPointMarker
        .addTo(map)
        .bindPopup("現在地", { autoClose: false })
        .openPopup();
    } else {
      map.setView([centerLatitude, centerLongitude], zoomLevel);
    }

    for (var prop in locationDataList) {
      var locationData = locationDataList[prop];
      var popupText = "";
      if (
        document.getElementById("areaMap") ||
        document.getElementById("gpsMap")
      ) {
        popupText = locationData["nameLink"];
      } else if (document.getElementById("medicalInstitutionMap")) {
        popupText = locationData["locationName"];
      } else {
        popupText = locationData["nameLink"] + "<br>" + locationData["status"];
      }
      var marker = L.marker([
        locationData["latitude"],
        locationData["longitude"],
      ]);
      if (document.getElementById("allMap")) {
        marker.addTo(map).bindPopup(popupText, {
          autoClose: false,
        });
      } else {
        marker
          .addTo(map)
          .bindPopup(popupText, { autoClose: false })
          .openPopup();
      }
    }
  },
  false
);
