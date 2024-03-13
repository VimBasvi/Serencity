// initialize the map and window
let map, infoWindow;
let infoWindows = [];
let clickMarker; // reuse the existing marker

function initMap() {

  const mapStyle = [
    {
        featureType: 'poi',  // Point of Interest
        elementType: 'labels',  // Hide labels
        stylers: [{ visibility: 'off' }]  // Set visibility off
    }
  ];
  
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 15,
    styles: mapStyle  
  });
  infoWindow = new google.maps.InfoWindow();

  // Click event listener
  map.addListener('click', function (e) {
    placeMarkerAndInfoWindow(e.latLng, map);

    // get latitude and longitude 
    const lat = e.latLng.lat();
    const lng = e.latLng.lng();

    // update hidden input fields 
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lng;
  });

  // HTML5 geolocation.
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };

        infoWindow.setPosition(pos);
        infoWindow.setContent('You are here.');
        infoWindow.open(map);
        map.setCenter(pos);
      },
      () => {
        handleLocationError(true, infoWindow, map.getCenter());
      }
    );
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }

  // call function to fetch location data from SQLite file and add markers
  fetchAndDisplayMarkers();
}


// Function to place a marker and open an InfoWindow
function placeMarkerAndInfoWindow(latLng, map) {
  // Clear the previous infoWindow if it exists
  if (infoWindow) {
    infoWindow.close();
  }

  // Check if marker already exists
  if (!clickMarker) {
  // Initialize the marker if it doesn't exist
  clickMarker = new google.maps.Marker({
      position: latLng,
      map: map
  });
} else {
    // move the existing marker to the new location
    clickMarker.setPosition(latLng);
}
  // Initialize the geocoder
  const geocoder = new google.maps.Geocoder();

  // Geocoding API to get the address from the latLng
  geocoder.geocode({ location: latLng }, (results, status) => {
    if (status === "OK") {
      console.log(results)
      if (results[0]) {
        const address = results[0].formatted_address;
        console.log(results)
        // Display InfoWindow with the formatted address
        infoWindow.setContent(address);
        infoWindow.open(map, clickMarker);

        // Update the address input field in the form
        document.getElementById('address').value = address;

        // Send the data to the Flask server to store in database
        // call function to send data to flask server
      
      } else {
        window.alert("No results found");
      }
    } else {
      window.alert("Geocoder failed due to: " + status);
    }
  });
}

// when clicked, populate the input box for address with the address set

// Function to send location data to the Flask server
// write function sendLocationToServer(locationData) 

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(
    browserHasGeolocation
      ? 'Error: The Geolocation service failed.'
      : "Error: Your browser doesn't support geolocation."
  );
  infoWindow.open(map);
}

// function to display markers on map
function fetchAndDisplayMarkers() {
  const locations = locationsData;

  // define SVG image as a data URL
  const svgIcon = 'data:image/svg+xml;charset=UTF-8;base64,' + btoa(`
  <svg xmlns="http://www.w3.org/2000/svg" height="16" width="12" viewBox="0 0 384 512">
      <path fill="#319637" d="M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/>
  </svg>
  `);

  // Loop through your locations and add a marker for each
  locations.forEach(location => {
    const { latitude, longitude, approx_address, name } = location;

    const marker = new google.maps.Marker({
      position: { lat: latitude, lng: longitude },
      map: map,
      title: name, // Display name as marker title
      icon: {
        url: svgIcon,
        title: name,
        scaledSize: new google.maps.Size(35, 35), 
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(20, 40),
      }

      });

    // displays infowindow on hover
    marker.addListener('mouseover', () => {
      const contentString = `
        <div class="info-window">
          <h3>${location.name}</h3>
          <p>${location.approx_address}</p>
          <a href="/spot_details/${location.id}">View Details</a>
        </div>
      `;
      // Display an info window when a marker is hovered
      const infoWindow = new google.maps.InfoWindow({
        content: contentString,
      });
      infoWindow.open(map, marker);
      infoWindows.push(infoWindow); // Add the info window to the array
    });
    
    marker.addListener('mouseout', () => {
      // Close all info windows when the cursor moves away from the marker
      infoWindows.forEach(window => {
        window.close();
      });
    });

    marker.addListener('click', () => {
      window.location.href = `/spot/${location.id}`; // Redirect to the spot_details page for the specific location
    });
  });
}



window.initMap = initMap;
