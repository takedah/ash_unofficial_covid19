document.addEventListener(
  "DOMContentLoaded",
  function () {
    const resultsLength = Number(
      JSON.parse(document.getElementById("results").dataset.length)
    );

    const map = L.map("mapid", { tap: false });
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
      var division = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.division
        )
      );
      var vaccine = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.vaccine
        )
      );
      var isTargetNotFamily = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .istargetnotfamily
        )
      );
      var status = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.status
        )
      );
      var parentPath = "reservation_status";
      var nameLink =
        "<a href='/" +
        parentPath +
        "/medical_institution/" +
        url +
        "'>" +
        locationName +
        "</a>";
      if (/True/.test(isTargetNotFamily)) {
        isTargetNotFamily =
          "<div class='mb-1 py-2'><span class='text-white bg-success p-2 rounded'>かかりつけ以外OK</span></div>";
      } else if (/False/.test(isTargetNotFamily)) {
        isTargetNotFamily =
          "<div class='mb-1 py-2'><span class='text-white bg-secondary p-2 rounded'>かかりつけ以外NG</span></div>";
      } else {
        isTargetNotFamily = "";
      }
      var statusMessage = "";
      if (locationDataList[locationName] === undefined) {
        if (division === "") {
          if (vaccine === "") {
            statusMessage =
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          } else {
            statusMessage =
              "<div class='mb-1'>" +
              vaccine +
              "</div>" +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          }
        } else {
          if (vaccine === "") {
            statusMessage =
              "<div class='mb-1 h6'>" +
              division +
              "</div>" +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          } else {
            statusMessage =
              "<div class='mb-1 h6'>" +
              division +
              "</div>" +
              "<div class='mb-1'>" +
              vaccine +
              "</div>" +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          }
        }
      } else {
        if (division === "") {
          if (vaccine === "") {
            statusMessage =
              locationDataList[locationName]["statusMessage"] +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          } else {
            statusMessage =
              locationDataList[locationName]["statusMessage"] +
              "<div class='mb-1'>" +
              vaccine +
              "</div>" +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          }
        } else {
          if (vaccine === "") {
            statusMessage =
              locationDataList[locationName]["statusMessage"] +
              "<div class='mb-1 h6'>" +
              division +
              "</div>" +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          } else {
            statusMessage =
              locationDataList[locationName]["statusMessage"] +
              "<div class='mb-1 h6'>" +
              division +
              "</div>" +
              "<div class='mb-1'>" +
              vaccine +
              "</div>" +
              "<div class='mb-1'>" +
              "予約開始時期: " +
              status +
              "</div>" +
              isTargetNotFamily;
          }
        }
      }
      locationDataList[locationName] = {
        locationName: locationName,
        latitude: latitude,
        longitude: longitude,
        nameLink: nameLink,
        statusMessage: statusMessage,
        isTargetNotFamily: isTargetNotFamily,
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

    var zoomLevel = 13;
    if (document.getElementById("areaMap")) {
      zoomLevel = 15;
    } else if (document.getElementById("gpsMap")) {
      zoomLevel = 14;
    } else if (document.getElementById("medicalInstitutionMap")){
      zoomLevel = 16;
    } else if (document.getElementById("divisionMap")){
      zoomLevel = 12;
    }

    if (document.getElementById("gpsMap")) {
      const currentLongitude = parseFloat(
        JSON.parse(document.getElementById("results").dataset.currentlongitude)
      );
      const currentLatitude = parseFloat(
        JSON.parse(document.getElementById("results").dataset.currentlatitude)
      );
      map.setView([currentLatitude, currentLongitude], zoomLevel);
      const currentPointCircle = L.circle([currentLatitude, currentLongitude], {
        radius: 150,
        weight: 0.3,
        color: "red",
        fillColor: "red",
        fillOpacity: 0.5,
      });
      currentPointCircle.addTo(map);
    } else {
      map.setView([centerLatitude, centerLongitude], zoomLevel);
    }

    const mapPrimaryIcon = L.divIcon({
      html: "<i class='fas fa-map-marker-alt'></i>",
      className: "map_primary_icon",
      iconAnchor: [14, 36],
      popupAnchor: [0, -22],
    });
    const mapWarningIcon = L.divIcon({
      html: "<i class='fas fa-map-marker-alt'></i>",
      className: "map_warning_icon",
      iconAnchor: [14, 36],
      popupAnchor: [0, -22],
    });

    const mapDangerIcon = L.divIcon({
      html: "<i class='fas fa-map-marker-alt'></i>",
      className: "map_danger_icon",
      iconAnchor: [14, 36],
      popupAnchor: [0, -22],
    });

    for (var prop in locationDataList) {
      var locationData = locationDataList[prop];
      var mapIcon = mapPrimaryIcon;
      var popupText = "";
      if (document.getElementById("medicalInstitutionMap")) {
        popupText =
          "<div class='h6'>" + locationData["locationName"] + "</div>";
      } else {
        popupText =
          "<div class='h6'>" +
          locationData["nameLink"] +
          "</div>" +
          locationData["statusMessage"];
      }
      var marker = L.marker(
        [locationData["latitude"], locationData["longitude"]],
        { icon: mapIcon }
      );
      if (document.getElementById("medicalInstitutionMap")) {
        marker
          .addTo(map)
          .bindPopup(popupText, {
            autoClose: false,
          })
          .openPopup();
      } else {
        marker.addTo(map).bindPopup(popupText, { autoClose: false });
      }
    }
  },
  false
);
