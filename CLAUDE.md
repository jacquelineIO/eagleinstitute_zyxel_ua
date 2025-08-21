# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zyxel USG Flex 200 captive portal application for guest WiFi that collects email addresses. The application runs on a Zyxel firewall and communicates with a Python backend server on Windows Server to store email data in CSV format.

## Development Commands

### Python Server (Primary)
```bash
# Windows
cd server
python captive_portal_server.py

# Or use batch file
run_server.bat

# macOS/Linux
cd server
python3 captive_portal_server.py
```


## Architecture

### System Design
- **Captive Portal**: HTML/CSS/JS hosted on Zyxel USG Flex 200
- **Backend Server**: Python HTTP server on Windows Server (192.168.50.19:8080)
- **Data Storage**: CSV file at C:\exports\export.csv
- **Communication**: Cross-origin POST requests from portal to backend

### Python Server (`server/captive_portal_server.py`)
- Lightweight HTTP server on port 8080
- Thread-safe email visit counting
- Endpoints:
  - `GET /` - Status page
  - `GET /health` - Health check JSON
  - `POST /append` - Email submission (expects `{"field1": "email"}`)
- Loads existing CSV data on startup to maintain counts
- Cross-platform support (Windows/Mac/Linux)

### Frontend Components
- **Portal Flow**: `ua_agree.html` → `ua_welcome.html`
- **JavaScript**: 
  - `script.js` - Frontend integration with Python backend (auto-detects environment)

### Deployment Flow
1. Guest connects to WiFi with password
2. Zyxel redirects to captive portal
3. User enters email on agreement page
4. JavaScript sends email to Python server
5. Python server writes to CSV
6. Portal submits to Zyxel for authentication
7. User granted internet access

## Key Technical Details

- **CORS**: Enabled on Python server for cross-origin requests
- **CSV Format**: Email Address,Date,Timestamp,Number of Visits
- **Visit Tracking**: Persistent across server restarts
- **Error Handling**: Validates email format, handles network failures
- **Windows Service**: Can run as service using NSSM

## Testing

### Local Testing
```bash
# Start Python server
cd server && python3 captive_portal_server.py

# Test endpoint
curl -X POST http://localhost:8080/append \
  -H "Content-Type: application/json" \
  -d '{"field1":"test@example.com"}'

# Serve HTML files
python3 -m http.server 8000
# Browse to http://localhost:8000/ua_agree.html
```

### Important Files to Modify
- `script.js`: Auto-detects environment (localhost vs production IP)
- `captive_portal_server.py`: Auto-detects platform for CSV path (Mac vs Windows)