# Bus Tracking Web Application

A complete real-time bus tracking application with Flask backend and vanilla JavaScript frontend using Google Maps API.

## Project Structure

```
bus-tracking-app/
├── backend/
│   ├── app.py              # Flask server with API endpoints
│   ├── routes.json         # Route data (backup)
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html         # Main HTML file
│   ├── styles.css        # CSS styles
│   └── script.js       # JavaScript logic
└── README.md          # This file
```

## Features

### Frontend
- Interactive full-screen Google Maps
- Route selection (5 predefined routes)
- Route visualization (blue polylines)
- Moving bus markers with icons
- Bus stop markers (red)
- User location marker (green)
- Directions route from user to nearest stop (green)
- Real-time bus info (speed, coordinates, ETA)
- Alerts/toast notifications
- Responsive design (mobile + desktop)

### Backend (Flask API)
- `/api/routes` - Get all routes
- `/api/routes/<id>` - Get route details
- `/api/bus-location/<id>` - Get bus positions
- `/api/bus-move/<id>` - Move buses (simulation)
- `/api/eta/<id>` - Get ETA to next stop
- `/api/nearest-stop` - Find nearest stop from user
- `/api/alerts/<id>` - Get arrival alerts
- `/api/control/pause/<id>` - Pause buses
- `/api/control/resume/<id>` - Resume buses
- Haversine formula for distance calculation

## Prerequisites

1. **Python 3.7+** installed
2. **Google Maps API Key** with these APIs enabled:
   - Maps JavaScript API
   - Directions API

## Setup Instructions

### Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Maps JavaScript API**
4. Enable **Directions API**
5. Create credentials (API key)
6. Copy the API key

### Step 2: Configure the Application

Open `frontend/index.html` and replace the API key:

```javascript
// Line ~90 in index.html
const GOOGLE_MAPS_API_KEY = 'YOUR_ACTUAL_API_KEY_HERE';
```

### Step 3: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run the Flask Server

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### Step 5: Run the Frontend

**Option A: Simple HTTP Server**

```bash
cd frontend
python -m http.server 8000
```

Then open `http://localhost:8000`

**Option B: Open Directly**

Simply open `frontend/index.html` in a browser (not recommended - some features may not work)

## Usage Guide

### Selecting a Route
1. Click on any route card (1-5) in the sidebar
2. The route will be drawn in blue on the map
3. Bus stops are marked in red

### Tracking the Bus
- The bus (orange marker) moves automatically every 2 seconds
- View speed, coordinates, and ETA in the sidebar

### Locating Yourself
1. Click **Locate Me** button
2. Allow browser geolocation permission
3. Your location appears (green marker)
4. Nearest bus stop is highlighted
5. Walking route to stop shown in green

### Controls
- **Pause/Play**: Stop or resume bus movement
- **Change Route**: Return to route selection

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/routes` | List all routes |
| GET | `/api/routes/<id>` | Get route details |
| GET | `/api/bus-location/<id>` | Get bus positions |
| POST | `/api/bus-move/<id>` | Move buses |
| GET | `/api/eta/<id>` | Get ETA data |
| POST | `/api/nearest-stop` | Find nearest stop |
| GET | `/api/alerts/<id>` | Get alerts |
| POST | `/api/control/pause/<id>` | Pause buses |
| POST | `/api/control/resume/<id>` | Resume buses |
| GET | `/api/health` | Health check |

## Color Legend

- **Blue (#4285f4)**: Selected bus route
- **Green (#34a853)**: User to bus stop route
- **Orange (#ff9800)**: Bus marker
- **Red (#ea4335)**: Bus stop markers
- **Green (#00ff88)**: User location marker

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python Flask
- **APIs**: Google Maps JavaScript API, Directions API
- **Geolocation**: Browser Geolocation API

## Troubleshooting

### Geolocation Not Working
- Use HTTPS or localhost
- Check browser permissions

### Map Not Loading
- Verify API key is correct
- Ensure APIs are enabled in Google Cloud Console

### Flask Connection Error
- Ensure Flask server is running on port 5000
- Check firewall settings

### CORS Errors
- Backend includes CORS support via flask-cors

## Demo Data

The app includes 5 routes in San Francisco:
1. **Route 1**: Downtown Express
2. **Route 2**: Financial District
3. **Route 3**: Mission Line
4. **Route 4**: Ocean Beach
5. **Route 5**: Twin Peaks

Each route has multiple stops and at least one bus.

## License

MIT License