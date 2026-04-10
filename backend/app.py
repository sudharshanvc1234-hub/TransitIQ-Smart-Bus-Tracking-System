"""
Bus Tracking Backend Server
Flask REST API for bus tracking application
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import math
import time
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ============================================
# ROUTE DATA - Mock data for 5 bus routes
# ============================================
ROUTES_DATA = {
    "route1": {
        "id": "route1",
        "name": "Downtown Express",
        "route_number": 1,
        "color": "#4285f4",
        "coordinates": [
            {"lat": 37.7749, "lng": -122.4194},
            {"lat": 37.7760, "lng": -122.4150},
            {"lat": 37.7780, "lng": -122.4100},
            {"lat": 37.7800, "lng": -122.4050},
            {"lat": 37.7820, "lng": -122.4000},
            {"lat": 37.7840, "lng": -122.3950},
            {"lat": 37.7860, "lng": -122.3900},
            {"lat": 37.7880, "lng": -122.3850}
        ],
        "stops": [
            {"id": "stop1", "name": "Market St & 1st", "lat": 37.7751, "lng": -122.4180},
            {"id": "stop2", "name": "Civic Center", "lat": 37.7795, "lng": -122.4139},
            {"id": "stop3", "name": "Van Ness Station", "lat": 37.7840, "lng": -122.4000},
            {"id": "stop4", "name": "Final Stop", "lat": 37.7880, "lng": -122.3850}
        ],
        "speed_kmh": 25
    },
    "route2": {
        "id": "route2",
        "name": "Financial District",
        "route_number": 2,
        "color": "#4285f4",
        "coordinates": [
            {"lat": 37.7950, "lng": -122.3950},
            {"lat": 37.7930, "lng": -122.3900},
            {"lat": 37.7900, "lng": -122.3850},
            {"lat": 37.7870, "lng": -122.3800},
            {"lat": 37.7840, "lng": -122.3750},
            {"lat": 37.7810, "lng": -122.3700},
            {"lat": 37.7780, "lng": -122.3650}
        ],
        "stops": [
            {"id": "stop1", "name": "Embarcadero", "lat": 37.7940, "lng": -122.3920},
            {"id": "stop2", "name": "Ferry Building", "lat": 37.7955, "lng": -122.3933},
            {"id": "stop3", "name": "Pier 39", "lat": 37.7887, "lng": -122.4098},
            {"id": "stop4", "name": "Fishermans Wharf", "lat": 37.8080, "lng": -122.4177}
        ],
        "speed_kmh": 20
    },
    "route3": {
        "id": "route3",
        "name": "Mission Line",
        "route_number": 3,
        "color": "#4285f4",
        "coordinates": [
            {"lat": 37.7700, "lng": -122.4300},
            {"lat": 37.7670, "lng": -122.4250},
            {"lat": 37.7640, "lng": -122.4200},
            {"lat": 37.7610, "lng": -122.4150},
            {"lat": 37.7580, "lng": -122.4100},
            {"lat": 37.7550, "lng": -122.4050},
            {"lat": 37.7520, "lng": -122.4000},
            {"lat": 37.7490, "lng": -122.3950}
        ],
        "stops": [
            {"id": "stop1", "name": "16th St Mission", "lat": 37.7650, "lng": -122.4200},
            {"id": "stop2", "name": "24th St Mission", "lat": 37.7522, "lng": -122.4182},
            {"id": "stop3", "name": "Cortland Ave", "lat": 37.7400, "lng": -122.4100},
            {"id": "stop4", "name": "Glen Park", "lat": 37.7330, "lng": -122.4330}
        ],
        "speed_kmh": 22
    },
    "route4": {
        "id": "route4",
        "name": "Ocean Beach",
        "route_number": 4,
        "color": "#4285f4",
        "coordinates": [
            {"lat": 37.7600, "lng": -122.4500},
            {"lat": 37.7650, "lng": -122.4550},
            {"lat": 37.7700, "lng": -122.4600},
            {"lat": 37.7750, "lng": -122.4650},
            {"lat": 37.7800, "lng": -122.4700},
            {"lat": 37.7850, "lng": -122.4750},
            {"lat": 37.7900, "lng": -122.4800}
        ],
        "stops": [
            {"id": "stop1", "name": "Castro Station", "lat": 37.7609, "lng": -122.4350},
            {"id": "stop2", "name": "Cole Valley", "lat": 37.7650, "lng": -122.4500},
            {"id": "stop3", "name": "Ocean Beach", "lat": 37.7594, "lng": -122.5107},
            {"id": "stop4", "name": "Outer Sunset", "lat": 37.7530, "lng": -122.4950}
        ],
        "speed_kmh": 18
    },
    "route5": {
        "id": "route5",
        "name": "Twin Peaks",
        "route_number": 5,
        "color": "#4285f4",
        "coordinates": [
            {"lat": 37.7800, "lng": -122.4400},
            {"lat": 37.7830, "lng": -122.4450},
            {"lat": 37.7860, "lng": -122.4500},
            {"lat": 37.7890, "lng": -122.4550},
            {"lat": 37.7920, "lng": -122.4600},
            {"lat": 37.7950, "lng": -122.4650},
            {"lat": 37.7980, "lng": -122.4700}
        ],
        "stops": [
            {"id": "stop1", "name": "Church & Market", "lat": 37.7820, "lng": -122.4320},
            {"id": "stop2", "name": "Twin Peaks", "lat": 37.7544, "lng": -122.4477},
            {"id": "stop3", "name": "Glen Park", "lat": 37.7330, "lng": -122.4330},
            {"id": "stop4", "name": "Balboa Park", "lat": 37.7190, "lng": -122.4470}
        ],
        "speed_kmh": 20
    }
}

# ============================================
# BUS STATE - Current state of buses
# ============================================
class BusState:
    def __init__(self, route_id, bus_id, start_index=0):
        self.route_id = route_id
        self.bus_id = bus_id
        self.current_index = start_index
        self.last_update = datetime.now()
        self.status = "active"  # active, paused

bus_states = {
    "route1": [BusState("route1", "bus1", 0), BusState("route1", "bus2", 4)],
    "route2": [BusState("route2", "bus1", 0)],
    "route3": [BusState("route3", "bus1", 0)],
    "route4": [BusState("route4", "bus1", 0)],
    "route5": [BusState("route5", "bus1", 0)]
}


# ============================================
# HAVERSINE FORMULA - Calculate distance between two coordinates
# ============================================
def haversine(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_eta(distance_km, speed_kmh):
    """
    Calculate ETA in minutes
    """
    if speed_kmh <= 0:
        return 0
    
    hours = distance_km / speed_kmh
    minutes = hours * 60
    
    return max(1, round(minutes))


# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """
    GET /routes
    Return all available bus routes
    """
    routes_list = []
    for route_id, route in ROUTES_DATA.items():
        routes_list.append({
            "id": route["id"],
            "name": route["name"],
            "route_number": route["route_number"],
            "stops": route["stops"],
            "coordinate_count": len(route["coordinates"])
        })
    
    return jsonify({
        "success": True,
        "routes": routes_list
    })


@app.route('/api/routes/<route_id>', methods=['GET'])
def get_route(route_id):
    """
    GET /routes/{route_id}
    Return details of a specific route
    """
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    
    return jsonify({
        "success": True,
        "route": route
    })


@app.route('/api/bus-location/<route_id>', methods=['GET'])
def get_bus_location(route_id):
    """
    GET /bus-location/{route_id}
    Return current bus coordinates for all buses on a route
    """
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    buses = bus_states.get(route_id, [])
    
    bus_locations = []
    for bus in buses:
        if bus.current_index < len(route["coordinates"]):
            coord = route["coordinates"][bus.current_index]
            bus_locations.append({
                "bus_id": bus.bus_id,
                "lat": coord["lat"],
                "lng": coord["lng"],
                "route_index": bus.current_index,
                "status": bus.status
            })
    
    return jsonify({
        "success": True,
        "route_id": route_id,
        "buses": bus_locations
    })


@app.route('/api/bus-location/<route_id>/<bus_id>', methods=['GET'])
def get_specific_bus_location(route_id, bus_id):
    """
    GET /bus-location/{route_id}/{bus_id}
    Return current location of a specific bus
    """
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    buses = bus_states.get(route_id, [])
    
    for bus in buses:
        if bus.bus_id == bus_id:
            if bus.current_index < len(route["coordinates"]):
                coord = route["coordinates"][bus.current_index]
                return jsonify({
                    "success": True,
                    "bus": {
                        "bus_id": bus.bus_id,
                        "route_id": bus.route_id,
                        "lat": coord["lat"],
                        "lng": coord["lng"],
                        "route_index": bus.current_index,
                        "status": bus.status
                    }
                })
    
    return jsonify({
        "success": False,
        "error": "Bus not found"
    }), 404


@app.route('/api/bus-move/<route_id>', methods=['POST'])
def move_bus(route_id):
    """
    POST /bus-move/{route_id}
    Move all buses on the specified route to the next position
    Used for simulation
    """
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    buses = bus_states.get(route_id, [])
    
    moved_buses = []
    for bus in buses:
        if bus.status == "active":
            bus.current_index += 1
            if bus.current_index >= len(route["coordinates"]):
                bus.current_index = 0  # Loop back to start
            
            coord = route["coordinates"][bus.current_index]
            moved_buses.append({
                "bus_id": bus.bus_id,
                "lat": coord["lat"],
                "lng": coord["lng"],
                "route_index": bus.current_index
            })
    
    return jsonify({
        "success": True,
        "route_id": route_id,
        "buses": moved_buses
    })


@app.route('/api/eta/<route_id>', methods=['GET'])
def get_eta(route_id):
    """
    GET /eta/{route_id}
    Return ETA for all buses on the route to their next stop
    """
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    buses = bus_states.get(route_id, [])
    speed = route["speed_kmh"]
    
    eta_data = []
    for bus in buses:
        if bus.current_index < len(route["coordinates"]):
            current_coord = route["coordinates"][bus.current_index]
            
            # Find next stop
            min_distance = float('inf')
            next_stop = None
            
            for stop in route["stops"]:
                distance = haversine(
                    current_coord["lat"], current_coord["lng"],
                    stop["lat"], stop["lng"]
                )
                if distance < min_distance:
                    min_distance = distance
                    next_stop = stop
            
            if next_stop:
                eta_minutes = calculate_eta(min_distance, speed)
                eta_data.append({
                    "bus_id": bus.bus_id,
                    "current_position": current_coord,
                    "next_stop": next_stop,
                    "distance_km": round(min_distance, 2),
                    "eta_minutes": eta_minutes,
                    "speed_kmh": speed
                })
    
    return jsonify({
        "success": True,
        "route_id": route_id,
        "eta_data": eta_data
    })


@app.route('/api/nearest-stop', methods=['POST'])
def get_nearest_stop():
    """
    POST /nearest-stop
    Find the nearest bus stop based on user location
    Request body: {"route_id": "route1", "user_lat": 37.7749, "user_lng": -122.4194}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided"
        }), 400
    
    route_id = data.get('route_id')
    user_lat = data.get('user_lat')
    user_lng = data.get('user_lng')
    
    if not all([route_id, user_lat, user_lng]):
        return jsonify({
            "success": False,
            "error": "Missing required fields"
        }), 400
    
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    stops = route["stops"]
    
    nearest_stop = None
    min_distance = float('inf')
    
    for stop in stops:
        distance = haversine(user_lat, user_lng, stop["lat"], stop["lng"])
        if distance < min_distance:
            min_distance = distance
            nearest_stop = stop
    
    if nearest_stop:
        return jsonify({
            "success": True,
            "nearest_stop": nearest_stop,
            "distance_km": round(min_distance, 2),
            "distance_meters": round(min_distance * 1000),
            "route_id": route_id
        })
    
    return jsonify({
        "success": False,
        "error": "No stops found"
    })


@app.route('/api/nearest-stop-from-bus', methods=['GET'])
def get_nearest_stop_from_bus():
    """
    GET /nearest-stop-from-bus?route_id=route1
    Find the nearest stop from the bus's current position
    """
    route_id = request.args.get('route_id')
    
    if not route_id or route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Invalid route_id"
        }), 400
    
    route = ROUTES_DATA[route_id]
    buses = bus_states.get(route_id, [])
    
    if not buses:
        return jsonify({
            "success": False,
            "error": "No buses on this route"
        }), 404
    
    bus = buses[0]
    current_coord = route["coordinates"][bus.current_index]
    speed = route["speed_kmh"]
    
    stops = route["stops"]
    nearest = None
    min_dist = float('inf')
    
    for stop in stops:
        dist = haversine(current_coord["lat"], current_coord["lng"], stop["lat"], stop["lng"])
        if dist < min_dist:
            min_dist = dist
            nearest = stop
    
    if nearest:
        return jsonify({
            "success": True,
            "bus_position": current_coord,
            "nearest_stop": nearest,
            "distance_km": round(min_dist, 2),
            "eta_minutes": calculate_eta(min_dist, speed),
            "alert": min_dist < 0.5  # Alert if within 500m
        })
    
    return jsonify({"success": False, "error": "No stops found"})


# ============================================
# ALERT SYSTEM
# ============================================

@app.route('/api/alerts/<route_id>', methods=['GET'])
def get_alerts(route_id):
    """
    GET /alerts/{route_id}
    Get any active alerts for the route
    """
    if route_id not in ROUTES_DATA:
        return jsonify({
            "success": False,
            "error": "Route not found"
        }), 404
    
    route = ROUTES_DATA[route_id]
    buses = bus_states.get(route_id, [])
    speed = route["speed_kmh"]
    
    alerts = []
    
    for bus in buses:
        current_coord = route["coordinates"][bus.current_index]
        
        for stop in route["stops"]:
            distance = haversine(
                current_coord["lat"], current_coord["lng"],
                stop["lat"], stop["lng"]
            )
            
            if distance < 0.5:
                eta = calculate_eta(distance, speed)
                if eta < 2:
                    alerts.append({
                        "type": "arriving",
                        "bus_id": bus.bus_id,
                        "stop_name": stop["name"],
                        "message": f"Bus {bus.bus_id} is arriving at {stop['name']} in {eta} minute(s)!",
                        "eta_minutes": eta
                    })
    
    return jsonify({
        "success": True,
        "route_id": route_id,
        "alerts": alerts
    })


# ============================================
# CONTROL ENDPOINTS
# ============================================

@app.route('/api/control/pause/<route_id>', methods=['POST'])
def pause_bus(route_id):
    """
    POST /control/pause/{route_id}
    Pause all buses on the route
    """
    if route_id not in bus_states:
        return jsonify({"success": False, "error": "Route not found"}), 404
    
    for bus in bus_states[route_id]:
        bus.status = "paused"
    
    return jsonify({"success": True, "message": f"Buses on {route_id} paused"})


@app.route('/api/control/resume/<route_id>', methods=['POST'])
def resume_bus(route_id):
    """
    POST /control/resume/{route_id}
    Resume all buses on the route
    """
    if route_id not in bus_states:
        return jsonify({"success": False, "error": "Route not found"}), 404
    
    for bus in bus_states[route_id]:
        bus.status = "active"
    
    return jsonify({"success": True, "message": f"Buses on {route_id} resumed"})


@app.route('/api/control/speed/<route_id>', methods=['POST'])
def set_bus_speed(route_id):
    """
    POST /control/speed/{route_id}
    Set speed for buses on the route
    Request body: {"speed": 30}
    """
    if route_id not in ROUTES_DATA:
        return jsonify({"success": False, "error": "Route not found"}), 404
    
    data = request.get_json()
    speed = data.get('speed', 25)
    
    ROUTES_DATA[route_id]['speed_kmh'] = speed
    
    return jsonify({
        "success": True,
        "route_id": route_id,
        "new_speed": speed
    })


# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("Bus Tracking API Server")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/routes              - Get all routes")
    print("  GET  /api/routes/<id>         - Get route details")
    print("  GET  /api/bus-location/<id> - Get bus locations")
    print("  POST /api/bus-move/<id>     - Move buses")
    print("  GET  /api/eta/<id>          - Get ETA data")
    print("  POST /api/nearest-stop      - Find nearest stop")
    print("  GET  /api/alerts/<id>       - Get alerts")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)