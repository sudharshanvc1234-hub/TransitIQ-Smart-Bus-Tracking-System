/**
 * Bus Tracking Frontend - JavaScript
 * Handles map display, API calls, and real-time updates
 */

// ============================================
// LOAD GOOGLE MAPS API
// ============================================

(function loadGoogleMaps() {
    const apiKey = typeof GOOGLE_MAPS_API_KEY !== 'undefined' ? GOOGLE_MAPS_API_KEY : '';
    
    if (!apiKey || apiKey === 'YOUR_API_KEY_HERE') {
        console.warn('Please set your Google Maps API key in index.html');
        return;
    }

    window.initMap = initMap;
    window.gm_authFailure = function() {
        showToast('Error', 'Google Maps API key is invalid');
        document.getElementById('loadingOverlay').classList.add('hidden');
    };

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
})();

// ============================================
// GLOBAL VARIABLES
// ============================================

let map;
let selectedRouteId = null;
let userLocation = null;
let isTracking = true;

// Map elements
let routePolyline = null;
let userRoutePolyline = null;
let busMarkers = [];
let stopMarkers = [];
let userMarker = null;
let nearestStopMarker = null;

// API instances
let directionsService = null;
let directionsRenderer = null;

// Movement interval
let movementInterval = null;
let checkInterval = null;

// ============================================
// INITIALIZATION
// ============================================

async function initMap() {
    try {
        // Initialize Google Map
        const center = { lat: 37.7749, lng: -122.4194 };
        
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: 13,
            center: center,
            styles: [
                { featureType: 'poi', elementType: 'labels', stylers: [{ visibility: 'off' }] }
            ],
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false
        });

        // Initialize Directions service
        directionsService = new google.maps.DirectionsService();
        directionsRenderer = new google.maps.DirectionsRenderer({
            suppressMarkers: true,
            preserveViewport: true,
            polylineOptions: {
                strokeColor: '#34a853',
                strokeWeight: 4,
                strokeOpacity: 0.8
            }
        });
        directionsRenderer.setMap(map);

        // Hide loading overlay
        document.getElementById('loadingOverlay').classList.add('hidden');

        // Load routes
        await loadRoutes();

    } catch (error) {
        console.error('Error initializing map:', error);
        showToast('Error', 'Failed to initialize map');
    }
}

// ============================================
// API FUNCTIONS
// ============================================

async function loadRoutes() {
    try {
        const response = await fetch(`${API_BASE_URL}/routes`);
        const data = await response.json();

        if (data.success) {
            renderRouteCards(data.routes);
        }
    } catch (error) {
        console.error('Error loading routes:', error);
        showToast('Error', 'Failed to load routes. Make sure Flask server is running.');
    }
}

async function getRouteDetails(routeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/routes/${routeId}`);
        const data = await response.json();
        return data.route || null;
    } catch (error) {
        console.error('Error getting route details:', error);
        return null;
    }
}

async function getBusLocation(routeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/bus-location/${routeId}`);
        const data = await response.json();
        return data.buses || [];
    } catch (error) {
        console.error('Error getting bus location:', error);
        return [];
    }
}

async function moveBus(routeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/bus-move/${routeId}`, {
            method: 'POST'
        });
        const data = await response.json();
        return data.buses || [];
    } catch (error) {
        console.error('Error moving bus:', error);
        return [];
    }
}

async function getETA(routeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/eta/${routeId}`);
        const data = await response.json();
        return data.eta_data || [];
    } catch (error) {
        console.error('Error getting ETA:', error);
        return [];
    }
}

async function getNearestStop(routeId, userLat, userLng) {
    try {
        const response = await fetch(`${API_BASE_URL}/nearest-stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                route_id: routeId,
                user_lat: userLat,
                user_lng: userLng
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error getting nearest stop:', error);
        return null;
    }
}

async function getAlerts(routeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/alerts/${routeId}`);
        const data = await response.json();
        return data.alerts || [];
    } catch (error) {
        console.error('Error getting alerts:', error);
        return [];
    }
}

async function pauseBus(routeId) {
    try {
        await fetch(`${API_BASE_URL}/control/pause/${routeId}`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error pausing bus:', error);
    }
}

async function resumeBus(routeId) {
    try {
        await fetch(`${API_BASE_URL}/control/resume/${routeId}`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error resuming bus:', error);
    }
}

// ============================================
// UI RENDERING
// ============================================

function renderRouteCards(routes) {
    const grid = document.getElementById('routeGrid');
    grid.innerHTML = '';

    routes.forEach(route => {
        const card = document.createElement('div');
        card.className = 'route-card';
        card.dataset.routeId = route.id;
        card.innerHTML = `
            <div class="route-number">${route.route_number}</div>
            <div class="route-name">${route.name}</div>
        `;
        card.onclick = () => selectRoute(route.id);
        grid.appendChild(card);
    });
}

// ============================================
// ROUTE SELECTION
// ============================================

async function selectRoute(routeId) {
    // Update selected route UI
    document.querySelectorAll('.route-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelector(`[data-route-id="${routeId}"]`).classList.add('active');

    // Clear previous map elements
    clearMapElements();

    // Set new route
    selectedRouteId = routeId;

    // Show sections
    document.getElementById('busInfoSection').style.display = 'block';
    document.getElementById('nearestSection').style.display = 'block';

    // Get route details from API
    const route = await getRouteDetails(routeId);
    if (!route) {
        showToast('Error', 'Failed to load route');
        return;
    }

    // Draw route polyline
    drawRoute(route);

    // Draw bus stops
    drawBusStops(route.stops);

    // Show legend
    document.getElementById('legend').style.display = 'block';

    // Start updating
    startUpdates(route);
}

function startUpdates(route) {
    // Clear existing intervals
    if (movementInterval) clearInterval(movementInterval);
    if (checkInterval) clearInterval(checkInterval);

    // Update bus position every 2 seconds
    movementInterval = setInterval(async () => {
        if (!isTracking || !selectedRouteId) return;
        
        const buses = await moveBus(selectedRouteId);
        updateBusMarkers(buses);
        updateBusInfo(buses, route);
    }, 2000);

    // Check ETA and alerts every second
    checkInterval = setInterval(async () => {
        if (!selectedRouteId) return;
        
        const etaData = await getETA(selectedRouteId);
        if (etaData.length > 0) {
            updateETA(etaData[0]);
        }
        
        // Check for alerts
        const alerts = await getAlerts(selectedRouteId);
        alerts.forEach(alert => {
            showToast(alert.type, alert.message);
        });
    }, 1000);

    // Initial update
    const buses = await getBusLocation(selectedRouteId);
    updateBusMarkers(buses);
    updateBusInfo(buses, route);
}

// ============================================
// MAP FUNCTIONS
// ============================================

function drawRoute(route) {
    // Draw route polyline
    routePolyline = new google.maps.Polyline({
        path: route.coordinates,
        geodesic: true,
        strokeColor: '#4285f4',
        strokeOpacity: 0.8,
        strokeWeight: 5
    });
    routePolyline.setMap(map);

    // Fit bounds
    const bounds = new google.maps.LatLngBounds();
    route.coordinates.forEach(coord => bounds.extend(coord));
    map.fitBounds(bounds);
}

function drawBusStops(stops) {
    stops.forEach(stop => {
        const marker = new google.maps.Marker({
            position: { lat: stop.lat, lng: stop.lng },
            map: map,
            icon: {
                path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z',
                fillColor: '#ea4335',
                fillOpacity: 1,
                strokeWeight: 0,
                scale: 1.2,
                anchor: new google.maps.Point(12, 17)
            },
            title: stop.name
        });
        stopMarkers.push(marker);
    });
}

function updateBusMarkers(buses) {
    // Clear existing bus markers
    busMarkers.forEach(marker => marker.setMap(null));
    busMarkers = [];

    // Add new markers
    buses.forEach(bus => {
        const marker = new google.maps.Marker({
            position: { lat: bus.lat, lng: bus.lng },
            map: map,
            icon: {
                path: 'M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-13c-.66 0-1.21.42-1.41 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99z',
                fillColor: '#ff9800',
                fillOpacity: 1,
                strokeWeight: 0,
                scale: 1.2,
                anchor: new google.maps.Point(12, 17)
            },
            title: bus.bus_id
        });
        busMarkers.push(marker);
    });
}

function clearMapElements() {
    if (routePolyline) {
        routePolyline.setMap(null);
        routePolyline = null;
    }
    if (userRoutePolyline) {
        userRoutePolyline.setMap(null);
        userRoutePolyline = null;
    }
    if (userMarker) {
        userMarker.setMap(null);
        userMarker = null;
    }
    if (nearestStopMarker) {
        nearestStopMarker.setMap(null);
        nearestStopMarker = null;
    }

    busMarkers.forEach(marker => marker.setMap(null));
    busMarkers = [];
    stopMarkers.forEach(marker => marker.setMap(null));
    stopMarkers = [];

    directionsRenderer.set('directions', null);

    if (movementInterval) {
        clearInterval(movementInterval);
        movementInterval = null;
    }
    if (checkInterval) {
        clearInterval(checkInterval);
        checkInterval = null;
    }
}

// ============================================
// USER LOCATION
// ============================================

function locateUser() {
    if (!navigator.geolocation) {
        showToast('Error', 'Geolocation not supported');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            // Add user marker
            if (userMarker) userMarker.setMap(null);
            
            userMarker = new google.maps.Marker({
                position: userLocation,
                map: map,
                icon: {
                    path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z',
                    fillColor: '#00ff88',
                    fillOpacity: 1,
                    strokeWeight: 0,
                    scale: 1,
                    anchor: new google.maps.Point(12, 17)
                },
                title: 'Your Location'
            });

            // Pan to user
            map.panTo(userLocation);

            // Find nearest stop
            if (selectedRouteId) {
                await findNearestStop();
            }
        },
        (error) => {
            console.error('Geolocation error:', error);
            showToast('Error', 'Unable to get location');
        }
    );
}

async function findNearestStop() {
    if (!selectedRouteId || !userLocation) return;

    const result = await getNearestStop(
        selectedRouteId,
        userLocation.lat,
        userLocation.lng
    );

    if (result && result.success) {
        // Update UI
        document.getElementById('nearestStopName').textContent = result.nearest_stop.name;
        
        const distance = result.distance_km < 1 
            ? `${result.distance_meters}m`
            : `${result.distance_km.toFixed(2)}km`;
        document.getElementById('nearestDistance').textContent = distance;

        // Add nearest stop marker if different from existing
        if (nearestStopMarker) nearestStopMarker.setMap(null);
        
        nearestStopMarker = new google.maps.Marker({
            position: { lat: result.nearest_stop.lat, lng: result.nearest_stop.lng },
            map: map,
            icon: {
                path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z',
                fillColor: '#00ff88',
                fillOpacity: 1,
                strokeWeight: 0,
                scale: 1.3,
                anchor: new google.maps.Point(12, 17)
            },
            title: result.nearest_stop.name
        });

        // Draw route from user to stop
        drawUserToStopRoute(result.nearest_stop);
    }
}

function drawUserToStopRoute(stop) {
    if (!userLocation) return;

    const request = {
        origin: userLocation,
        destination: { lat: stop.lat, lng: stop.lng },
        travelMode: 'WALKING'
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);
        } else {
            // Fallback to simple line
            userRoutePolyline = new google.maps.Polyline({
                path: [userLocation, { lat: stop.lat, lng: stop.lng }],
                geodesic: true,
                strokeColor: '#34a853',
                strokeOpacity: 0.8,
                strokeWeight: 4
            });
            userRoutePolyline.setMap(map);
        }
    });
}

// ============================================
// UI UPDATES
// ============================================

function updateBusInfo(buses, route) {
    if (buses.length === 0) return;

    const bus = buses[0];
    document.getElementById('busId').textContent = bus.bus_id;
    document.getElementById('busSpeed').textContent = `${route.speed_kmh} km/h`;
    document.getElementById('busLat').textContent = bus.lat.toFixed(6);
    document.getElementById('busLng').textContent = bus.lng.toFixed(6);
}

function updateETA(etaData) {
    if (etaData) {
        document.getElementById('busEta').textContent = `${etaData.eta_minutes} min`;
    }
}

function toggleTracking() {
    isTracking = !isTracking;
    
    const btn = document.getElementById('trackBtn');
    const statusBadge = document.getElementById('busStatus');
    
    if (isTracking) {
        btn.innerHTML = '⏸ Pause';
        statusBadge.textContent = 'Active';
        statusBadge.classList.remove('paused');
        if (selectedRouteId) resumeBus(selectedRouteId);
    } else {
        btn.innerHTML = '▶ Play';
        statusBadge.textContent = 'Paused';
        statusBadge.classList.add('paused');
        if (selectedRouteId) pauseBus(selectedRouteId);
    }
}

function showRouteSelector() {
    // Clear and reset
    clearMapElements();
    selectedRouteId = null;
    
    // Reset UI
    document.querySelectorAll('.route-card').forEach(card => {
        card.classList.remove('active');
    });
    
    document.getElementById('busInfoSection').style.display = 'none';
    document.getElementById('nearestSection').style.display = 'none';
    document.getElementById('legend').style.display = 'none';
    
    // Reset map center
    map.setCenter({ lat: 37.7749, lng: -122.4194 });
    map.setZoom(13);
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

let toastTimeout = null;

function showToast(title, message) {
    const toast = document.getElementById('toast');
    const titleEl = document.getElementById('toastTitle');
    const messageEl = document.getElementById('toastMessage');
    
    titleEl.textContent = title.charAt(0).toUpperCase() + title.slice(1);
    messageEl.textContent = message;
    
    toast.classList.add('show');
    
    if (toastTimeout) clearTimeout(toastTimeout);
    
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatDistance(distanceKm) {
    if (distanceKm < 1) {
        return `${Math.round(distanceKm * 1000)}m`;
    }
    return `${distanceKm.toFixed(2)}km`;
}