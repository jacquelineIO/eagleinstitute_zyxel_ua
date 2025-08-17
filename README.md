# Zyxel USG Flex 200 Captive Portal Application

A guest WiFi captive portal application designed for Zyxel USG Flex 200 firewall that collects email addresses from guest users accessing the network.

## Overview

This application provides a captive portal page for guest WiFi users. When guests connect to the WiFi (after entering the network password), they are presented with a terms of service page where they must enter their email address to gain internet access. The application tracks:
- Email addresses
- Date and timestamp of each visit
- Number of visits per email

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│                Guest Device                      │
│              (Phone/Laptop/Tablet)                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│           Zyxel USG Flex 200 Firewall           │
│                                                  │
│  ┌───────────────────────────────────────┐      │
│  │   Captive Portal (HTML/CSS/JS)        │      │
│  │   - ua_agree.html (desktop)           │      │
│  │   - ua_agree_m.html (mobile)          │      │
│  │   - ua_welcome.html (success pages)   │      │
│  └───────────────┬───────────────────────┘      │
└──────────────────┼──────────────────────────────┘
                   │ HTTP POST to :8080/append
                   ▼
┌─────────────────────────────────────────────────┐
│          Windows Server (192.168.50.19)          │
│                                                  │
│  ┌───────────────────────────────────────┐      │
│  │   Python Server (Port 8080)           │      │
│  │   - Receives email submissions        │      │
│  │   - Tracks visit counts               │      │
│  │   - Writes to CSV file                │      │
│  └───────────────┬───────────────────────┘      │
│                  │                               │
│                  ▼                               │
│  ┌───────────────────────────────────────┐      │
│  │   C:\export\export.csv                │      │
│  │   Email,Date,Timestamp,Visits         │      │
│  └───────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

### Application Flow

1. **Guest connects to WiFi** → Enters WiFi password
2. **Captive portal loads** → Zyxel redirects to ua_agree.html
3. **User enters email** → JavaScript validates email format
4. **Form submission** → 
   - JavaScript sends email to Python server (port 8080)
   - Python server writes to CSV file
   - Original form submits to Zyxel for authentication
5. **Success** → User redirected to ua_welcome.html and granted internet access

## File Structure

```
zyxel-ua/
├── README.md                 # This file
├── CLAUDE.md                # AI assistant documentation
├── .gitignore              # Git ignore rules
│
├── server/                  # Python backend server
│   ├── captive_portal_server.py  # Main Python server
│   ├── run_server.bat           # Windows batch file to start server
│   └── config.js               # JavaScript configuration
│
├── Portal Pages (uploaded to Zyxel):
│   ├── ua_agree.html        # Desktop agreement page
│   ├── ua_agree_m.html      # Mobile agreement page
│   ├── ua_welcome.html      # Desktop success page
│   ├── ua_welcome_m.html    # Mobile success page
│   ├── script.js           # JavaScript for Python backend
│   ├── ua.css              # Desktop styles
│   └── css_m/              # Mobile styles
│
└── Assets:
    ├── images/             # Desktop images
    └── images_m/           # Mobile images

```

## Setup Instructions

### Prerequisites

- **Windows Server**: Windows Server 2016 or later
- **Python**: Version 3.7 or higher
- **Network Access**: Server must be accessible from Zyxel firewall (192.168.50.19)
- **Permissions**: Write access to C:\export directory

### Windows Server Setup

1. **Install Python**
   ```cmd
   # Download from https://www.python.org/downloads/
   # During installation, check "Add Python to PATH"
   ```

2. **Create export directory**
   ```cmd
   mkdir C:\export
   ```

3. **Copy server files**
   - Copy the `server` folder to a location like `C:\captive_portal\`
   - Ensure `captive_portal_server.py` and `run_server.bat` are present

4. **Start the server**
   ```cmd
   cd C:\captive_portal\server
   run_server.bat
   ```

5. **Configure as Windows Service (Optional - Recommended for Production)**

   ### Why Run as a Service?
   
   **Current Method (run_server.bat):**
   - ✅ **Pros:**
     - Simple to start and stop
     - Easy to see console output for debugging
     - Quick to test changes
     - No additional software needed
   - ❌ **Cons:**
     - Must manually start after server reboot
     - Stops if user logs off
     - Command window must stay open
     - No automatic restart on crashes
   
   **Windows Service Method:**
   - ✅ **Pros:**
     - Starts automatically with Windows
     - Runs in background (no window needed)
     - Continues running after logoff
     - Auto-restart on failure
     - Runs with system privileges
     - Professional deployment approach
   - ❌ **Cons:**
     - Harder to debug (logs go to files)
     - Requires NSSM installation
     - More complex to update
     - Need admin rights to manage

   ### Installing as Windows Service with NSSM

   **Step 1: Download NSSM**
   - Download from: https://nssm.cc/download
   - Extract to `C:\nssm\` (or any permanent location)
   - Add to PATH or use full path to nssm.exe

   **Step 2: Install the Service**
   ```cmd
   # Open Command Prompt as Administrator
   cd C:\nssm\win64\  (or win32 for 32-bit)
   
   # Install service interactively (recommended)
   nssm install CaptivePortal
   
   # Or install via command line
   nssm install CaptivePortal "C:\Python39\python.exe" "C:\captive_portal\server\captive_portal_server.py"
   ```

   **Step 3: Configure Service Settings (Interactive Mode)**
   - **Application tab:**
     - Path: `C:\Python39\python.exe` (your Python path)
     - Startup directory: `C:\captive_portal\server\`
     - Arguments: `captive_portal_server.py`
   
   - **Details tab:**
     - Display name: `Captive Portal Email Collector`
     - Description: `Collects emails from Zyxel guest WiFi portal`
     - Startup type: `Automatic`
   
   - **I/O tab (for logging):**
     - Output: `C:\captive_portal\logs\service.log`
     - Error: `C:\captive_portal\logs\error.log`
   
   - **File rotation tab:**
     - Check "Replace existing output and error files"
     - Or configure rotation for log management

   **Step 4: Start and Manage Service**
   ```cmd
   # Start the service
   nssm start CaptivePortal
   # Or use Windows Services: net start CaptivePortal
   
   # Stop the service
   nssm stop CaptivePortal
   
   # Restart the service
   nssm restart CaptivePortal
   
   # Check service status
   nssm status CaptivePortal
   
   # Remove service (if needed)
   nssm remove CaptivePortal confirm
   ```

   **Step 5: Configure Auto-Restart on Failure**
   ```cmd
   # Set service to restart on failure
   nssm set CaptivePortal AppExit Default Restart
   nssm set CaptivePortal AppRestartDelay 5000  # 5 seconds delay
   
   # Or use Windows SC command
   sc failure CaptivePortal reset=0 actions=restart/5000
   ```

   ### Monitoring the Service

   **View Logs:**
   ```cmd
   # Check service logs
   type C:\captive_portal\logs\service.log
   
   # Monitor in real-time (PowerShell)
   Get-Content C:\captive_portal\logs\service.log -Wait
   ```

   **Windows Event Viewer:**
   - Open Event Viewer → Windows Logs → Application
   - Filter by Source: "CaptivePortal"

   **Service Management GUI:**
   - Run `services.msc`
   - Find "Captive Portal Email Collector"
   - Right-click for Start/Stop/Restart options

   ### Recommendation
   
   **For Development/Testing:** Use `run_server.bat` for immediate feedback and debugging
   
   **For Production:** Use NSSM Windows Service for reliability and automatic operation

### Zyxel USG Flex 200 Configuration

1. **Prepare portal files for upload**:
   - Verify server IP in `script.js` (auto-detects localhost vs production):
     ```javascript
     const PYTHON_SERVER_URL = isLocal 
       ? 'http://localhost:8080/append'
       : 'http://192.168.50.19:8080/append';
     ```

2. **Create ZIP package**:
   - Include: HTML files, CSS, JavaScript, images
   - Structure should match Zyxel requirements

3. **Upload to Zyxel**:
   - Access Zyxel admin interface
   - Navigate to Captive Portal settings
   - Upload the ZIP file
   - Configure guest network to use the captive portal

## Running Locally for Testing

### Quick Start (All Platforms)

We provide convenient scripts to run both servers together:

**Windows:**
```cmd
run_local.bat
```

**macOS/Linux:**
```bash
python3 run_local.py
```

This will:
- Start the Python API server on port 8080
- Start an HTML server on port 8000
- Automatically open your browser to the portal page
- Handle localhost configuration automatically

### Manual Setup (Two Terminal Windows)

#### Terminal 1: Start Python API Server

**Windows:**
```cmd
cd server
python captive_portal_server.py
```

**macOS/Linux:**
```bash
cd server
python3 captive_portal_server.py
```

#### Terminal 2: Serve HTML Files

**All Platforms:**
```bash
# From the main ua directory
python3 -m http.server 8000
# Or for Python 2: python -m SimpleHTTPServer 8000
```

#### Configure for Localhost

The `script.js` file automatically detects the environment:
```javascript
// Production setting
const PYTHON_SERVER_URL = 'http://192.168.50.19:8080/append';

// Change to localhost for testing
const PYTHON_SERVER_URL = 'http://localhost:8080/append';
```

#### Access the Application

Open your browser to:
- Desktop version: http://localhost:8000/ua_agree.html
- Mobile version: http://localhost:8000/ua_agree_m.html
- API health check: http://localhost:8080/health

### Testing the Complete Flow

1. **Start both servers** (using run_local script or manually)

2. **Open the portal page** in your browser

3. **Fill in an email address** and submit

4. **Check the CSV file** was created:
   ```bash
   # macOS/Linux
   cat export/export.csv
   
   # Windows
   type export\export.csv
   ```

5. **Verify the API directly**:
   ```bash
   # Test health endpoint
   curl http://localhost:8080/health
   
   # Submit test email
   curl -X POST http://localhost:8080/append \
     -H "Content-Type: application/json" \
     -d '{"field1":"test@example.com"}'
   ```

### Development Tips

1. **Browser Console**: Open Developer Tools (F12) to see any JavaScript errors

2. **Network Tab**: Check if requests to the Python server are successful

3. **Server Logs**: Both servers will output logs to the terminal

4. **Clear Cache**: Use Ctrl+F5 to force refresh if changes aren't showing

5. **CORS Issues**: The Python server includes CORS headers, but if you still have issues, try:
   - Using Chrome with `--disable-web-security` flag (development only!)
   - Or use Firefox which is generally more permissive for localhost

### File Locations During Testing

| File | Purpose | Location |
|------|---------|----------|
| CSV Output | Email data | `./export/export.csv` (local) or `C:\export\export.csv` (production) |
| Python Server | API backend | `http://localhost:8080` |
| HTML Server | Serves portal pages | `http://localhost:8000` |
| Portal Page | User-facing form | `http://localhost:8000/ua_agree.html` |

## Python Server Details

### Endpoints

- `GET /` - Server status page
- `GET /health` - JSON health check endpoint
- `POST /append` - Email submission endpoint
  - Request body: `{"field1": "email@example.com"}`
  - Response: "Data appended successfully" or error

### Features

- **Thread-safe** email counting
- **Cross-platform** support (Windows/Mac/Linux)
- **CORS enabled** for cross-origin requests
- **Persistent tracking** - loads existing counts on startup
- **CSV format**: Email Address,Date,Timestamp,Number of Visits

### CSV Output Format

```csv
Email Address,Date,Timestamp,Number of Visits
john@example.com,11/16/2024,02:30:45 PM,1
jane@example.com,11/16/2024,02:35:12 PM,1
john@example.com,11/16/2024,03:15:22 PM,2
```

## Common Issues and Solutions

### Issue 1: Python server can't write to C:\export

**Solution**: Ensure the directory exists and the Python process has write permissions:
```cmd
mkdir C:\export
icacls C:\export /grant Everyone:F
```

### Issue 2: Captive portal shows but doesn't save emails

**Possible causes**:
1. **Server not running**: Check if Python server is running on port 8080
2. **Firewall blocking**: Add Windows Firewall rule:
   ```cmd
   netsh advfirewall firewall add rule name="Captive Portal" dir=in action=allow protocol=TCP localport=8080
   ```
3. **Wrong IP in JavaScript**: Verify server IP in script.js (should auto-detect)

### Issue 3: CORS errors in browser console

**Solution**: The Python server includes CORS headers. If still having issues:
- Check browser console for specific error
- Ensure Zyxel isn't blocking cross-origin requests
- Test with `curl` to bypass browser CORS

### Issue 4: Email counts reset after server restart

**Solution**: The server loads existing CSV on startup. Ensure:
- CSV file path is correct
- File isn't being deleted/moved
- Server has read permissions

### Issue 5: Multiple server instances

**Solution**: Only run one instance to avoid port conflicts:
```cmd
# Check if port 8080 is in use
netstat -an | findstr :8080

# Kill existing Python processes if needed
taskkill /F /IM python.exe
```

## Security Considerations

1. **Network Isolation**: Keep the Windows server on a separate VLAN from guest network
2. **HTTPS**: Consider implementing SSL/TLS for production
3. **Input Validation**: Server validates email format
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse
5. **Data Privacy**: Implement data retention policies for collected emails
6. **Access Control**: Restrict access to export folder and CSV files

## Monitoring

Check server health:
```bash
curl http://192.168.50.19:8080/health
```

View server logs:
- Windows: Check console output or redirect to file
- Service: Check Windows Event Viewer

Monitor CSV file:
```cmd
type C:\export\export.csv
```

## Support

For issues with:
- **Zyxel configuration**: Consult Zyxel USG Flex 200 documentation
- **Python server**: Check server console output for errors
- **Network connectivity**: Verify firewall rules and routing

## Git Line Endings (CRLF/LF)

This repository uses CRLF line endings since it's primarily deployed on Windows Server. When cloning or contributing:

### For Windows Users
```bash
# Keep CRLF endings (recommended for this project)
git config core.autocrlf true
```

### For Mac/Linux Users
```bash
# Convert to LF locally but commit as CRLF
git config core.autocrlf input
```

### Why CRLF?
- **Primary Platform**: The Python server runs on Windows Server
- **Batch Files**: `.bat` files require CRLF to execute properly on Windows
- **CSV Files**: Windows Excel expects CRLF in CSV files
- **Consistency**: Maintains compatibility with Windows-based Zyxel management tools

### File-Specific Line Endings
- **Batch files** (`.bat`): Must use CRLF for Windows
- **Python files** (`.py`): Work with both CRLF and LF
- **Web files** (`.html`, `.js`, `.css`): Work with both, but typically use LF
- **CSV exports**: Use CRLF for Windows Excel compatibility

If you encounter line ending issues:
```bash
# Check current setting
git config core.autocrlf

# View file line endings
file server/run_server.bat  # On Mac/Linux
# Should show: "ASCII text, with CRLF line terminators"
```

## License

Internal use only - The Eagle Institute / Air University Innovation Accelerator (AUiX)