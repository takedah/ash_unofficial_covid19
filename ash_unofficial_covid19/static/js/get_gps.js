function getLocation() {
  var nudge = document.getElementById("nudge");
  var searchByGps = document.getElementById("searchByGps");
  var gpsServiceStatus = document.getElementById("gpsServiceStatus");

  var showNudgeButton = function () {
    nudge.style.display = "block";
  };
  var hideNudgeButton = function () {
    nudge.style.display = "none";
  };
  var showSearchForm = function () {
    searchByGps.style.display = "block";
  };
  var hideSearchForm = function () {
    searchByGps.style.display = "none";
  };

  function setGpsServiceStatus(message) {
    if (message == "") {
      gpsServiceStatus.className = "none";
    } else {
      gpsServiceStatus.className = "alert alert-danger";
    }
    gpsServiceStatus.innerHTML = message;
  }

  if (navigator.geolocation) {
    function geoSuccess(position) {
      setGpsServiceStatus("");
      hideNudgeButton();
      showSearchForm();
      var currentLatitude = position.coords.latitude;
      var currentLongitude = position.coords.longitude;
      document.getElementById("currentLatitude").value = currentLatitude;
      document.getElementById("currentLongitude").value = currentLongitude;
    }

    function geoError(error) {
      var errorCode = error.code;
      const PERMISSION_DENIED = 1;
      const TIMEOUT = 2;
      const POSITION_UNAVAILAVLE = 3;

      hideSearchForm();
      showNudgeButton();

      switch (errorCode) {
        case TIMEOUT:
          setGpsServiceStatus(
            "タイムアウトしました。しばらく待ってから再度お試しください。"
          );
          break;
        case PERMISSION_DENIED:
          setGpsServiceStatus("位置情報の取得を許可して再度お試しください。");
          break;
        case POSITION_UNAVAILAVLE:
          setGpsServiceStatus(
            "位置情報の取得中にエラーが発生しました。再度お試しください。"
          );
          break;
      }
    }

    navigator.geolocation.getCurrentPosition(geoSuccess, geoError);
  } else {
    setGpsServiceStatus("お使いの環境では位置情報を取得できませんでした。");
  }
}

document.addEventListener(
  "DOMContentLoaded",
  function () {
    document.getElementById("gpsServiceStatus").innerHTML = "";
    document.getElementById("searchByGps").style.display = "none";
    document
      .getElementById("useGps")
      .addEventListener("click", getLocation, false);
  },
  false
);
