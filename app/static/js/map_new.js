// Initialize map for complaint form
function initComplaintMap() {
    console.log('initComplaintMap called');
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded!');
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.innerHTML = '<div style="padding: 20px; color: red; text-align: center;">Error: Leaflet library not loaded. Please refresh the page.</div>';
        }
        return;
    }

    // Get map container
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container not found!');
        return;
    }

    // Initialize the map centered on India with city-level zoom and zoom limits
    var map = L.map('map', {
        minZoom: 5,
        maxZoom: 18
    }).setView([20.5937, 78.9629], 13);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Try to center on user's location if available
    map.locate({ setView: true, maxZoom: 15 });

    function onLocationFound(e) {
        L.marker(e.latlng).addTo(map)
            .bindPopup("You are here")
            .openPopup();
    }
    map.on('locationfound', onLocationFound);

    var marker;

    // Handle map click events
    map.on('click', function (e) {
        console.log('map clicked', e.latlng);
        var lat = e.latlng.lat;
        var lng = e.latlng.lng;

        // Remove existing marker if any
        if (marker) {
            map.removeLayer(marker);
        }

        // Add new marker
        marker = L.marker([lat, lng]).addTo(map)
            .bindPopup("Selected Location")
            .openPopup();

        // Update hidden form fields
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;

        // Update status message
        const statusElement = document.getElementById('map-status');
        if (statusElement) {
            statusElement.textContent = 'Location Selected';
            statusElement.style.color = 'green';
        }
    });

    // Fix rendering issues on load
    setTimeout(function () {
        map.invalidateSize();
    }, 300);

    // Make map responsive on resize
    window.addEventListener('resize', function () {
        map.invalidateSize();
    });
}

// Ensure initialization runs even if script loads after DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComplaintMap);
} else {
    initComplaintMap();
}