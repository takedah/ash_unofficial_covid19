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
      var url = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.url
        )
      );
      var address = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset.address
        )
      );
      var latitude = JSON.parse(
        document.getElementById("order" + currentOrder).dataset.latitude
      );
      var longitude = JSON.parse(
        document.getElementById("order" + currentOrder).dataset.longitude
      );
      var isTargetNotFamily = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .istargetnotfamily
        )
      );
      var isPediatrics = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .ispediatrics
        )
      );
      var mon = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .mon
        )
      );
      var tue = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .tue
        )
      );
      var wed = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .wed
        )
      );
      var thu = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .thu
        )
      );
      var fri = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .fri
        )
      );
      var sat = JSON.parse(
        JSON.stringify(
          document.getElementById("order" + currentOrder).dataset
            .sat
        )
      );
      var parentPath = "outpatient";
      var nameLink =
        "<a href='/" +
        parentPath +
        "/medical_institution/" +
        url +
        "'>" +
        locationName +
        "</a>";
      var isTargetNotFamilySign = ""
      if (/True/.test(isTargetNotFamily)) {
        isTargetNotFamilySign =
          "<span class='text-white bg-success p-2 rounded'>かかりつけ以外OK</span>";
      } else if (/False/.test(isTargetNotFamily)) {
        isTargetNotFamilySign =
          "<span class='text-white bg-secondary p-2 rounded'>かかりつけ以外NG</span>";
      }
      if (/True/.test(isPediatrics)) {
        isPediatricsSign =
          "<span class='text-white bg-success p-2 rounded'>小児対応OK</span>";
      } else {
        isPediatricsSign = "";
      }
      var statusMessage =
        "<div class='pb-2'>" + address + "</div>" +
        "<div class='pb-2'>" +
        "<div class='h6'>診療時間</div>" +
        "<div>月曜日: " + mon + "</div>" +
        "<div>火曜日: " + tue + "</div>" +
        "<div>水曜日: " + wed + "</div>" +
        "<div>木曜日: " + thu + "</div>" +
        "<div>金曜日: " + fri + "</div>" +
        "<div>土曜日: " + sat + "</div>" +
        "</div>" +
        "<div class='py-2'>" +
        isTargetNotFamilySign +
        " " +
        isPediatricsSign +
        "</div>";
      if (locationDataList[locationName] != undefined) {
            statusMessage = locationDataList[locationName]["statusMessage"] + statusMessage;
      }
      locationDataList[locationName] = {
        locationName: locationName,
        latitude: latitude,
        longitude: longitude,
        nameLink: nameLink,
        statusMessage: statusMessage,
        isTargetNotFamily: isTargetNotFamily,
        isPediatrics: isPediatrics,
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
    if (document.getElementById("gpsMap")) {
      zoomLevel = 14;
    } else if (document.getElementById("medicalInstitutionMap")){
      zoomLevel = 16;
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
      var mapIcon = mapWarningIcon;
      if (/True/.test(locationData["isTargetNotFamily"])) {
        mapIcon = mapPrimaryIcon;
      }
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
