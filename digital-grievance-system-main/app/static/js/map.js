// Initialize map for complaint form
document.addEventListener('DOMContentLoaded', function () {
    console.log('Initializing map...');

    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded!');
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.innerHTML = '<div style="padding: 20px; color: red; text-align: center;">Error: Leaflet library not loaded. Please refresh the page.</div>';
        }
        return;
    }

    console.log('Leaflet library loaded successfully');

    // Get map container
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container not found!');
        return;
    }

    try {
        // Initialize the map centered on Hyderabad (17.3850, 78.4867)
        var map = L.map('map').setView([17.3850, 78.4867], 13);
        console.log('Map object created successfully');

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
        console.log('Tiles added successfully');

        var marker;

        // Handle map click events to place marker and save coordinates
        map.on('click', function (e) {
            console.log('Map clicked at:', e.latlng);

            var lat = e.latlng.lat;
            var lng = e.latlng.lng;

            // Remove existing marker if any
            if (marker) {
                map.removeLayer(marker);
            }

            // Add new marker at clicked location
            marker = L.marker([lat, lng]).addTo(map)
                .bindPopup("Location: " + lat.toFixed(4) + ", " + lng.toFixed(4))
                .openPopup();

            // Store latitude and longitude in hidden form fields
            document.getElementById('latitude').value = lat;
            document.getElementById('longitude').value = lng;

            console.log('Marker placed and coordinates saved:', lat, lng);
        });

        console.log('Map initialization complete');

    } catch (error) {
        console.error('Map initialization error:', error);
        // Show error in container
        mapContainer.innerHTML = '<div style="padding: 20px; color: red; text-align: center;">Error loading map: ' + error.message + '</div>';
    }

    // Make map responsive
    window.addEventListener('resize', function () {
        if (typeof map !== 'undefined') {
            map.invalidateSize();
        }
    });

    // Force resize after a short delay to ensure proper rendering
    setTimeout(function () {
        if (typeof map !== 'undefined') {
            map.invalidateSize();
            console.log('Map resized');
        }
    }, 100);
});