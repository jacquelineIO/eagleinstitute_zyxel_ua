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
├── package.json             # Node.js dependencies (legacy)
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
│   ├── script_python.js     # JavaScript for Python backend
│   ├── ua.css              # Desktop styles
│   └── css_m/              # Mobile styles
│
├── Assets:
│   ├── images/             # Desktop images
│   └── images_m/           # Mobile images
│
└── Legacy Node.js (deprecated):
    ├── server.js           # Original Node.js server
    └── script.js           # Original JavaScript

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

5. **Configure as Windows Service (Optional)**
   ```cmd
   # Install NSSM (Non-Sucking Service Manager)
   nssm install CaptivePortal "C:\Python39\python.exe" "C:\captive_portal\server\captive_portal_server.py"
   nssm start CaptivePortal
   ```

### Zyxel USG Flex 200 Configuration

1. **Prepare portal files for upload**:
   - Update `script_python.js` with your server IP:
     ```javascript
     const PYTHON_SERVER_URL = 'http://192.168.50.19:8080/append';
     ```
   - In HTML files, change script reference:
     ```html
     <script src="script_python.js"></script>
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

### On Windows

1. **Install Python** (if not already installed)

2. **Modify server path** in `captive_portal_server.py`:
   ```python
   CSV_FILE_PATH = r'.\export\export.csv'  # Local path
   ```

3. **Run the server**:
   ```cmd
   cd server
   python captive_portal_server.py
   ```

4. **Test with browser**:
   - Open `ua_agree.html` in browser
   - Update JavaScript to point to localhost:
     ```javascript
     const PYTHON_SERVER_URL = 'http://localhost:8080/append';
     ```

### On macOS

1. **Install Python 3** (usually pre-installed):
   ```bash
   python3 --version
   ```

2. **Run the server**:
   ```bash
   cd server
   python3 captive_portal_server.py
   ```

3. **Test the endpoints**:
   ```bash
   # Check server health
   curl http://localhost:8080/health
   
   # Submit test email
   curl -X POST http://localhost:8080/append \
     -H "Content-Type: application/json" \
     -d '{"field1":"test@example.com"}'
   ```

4. **Open HTML locally**:
   ```bash
   # Start a simple HTTP server for HTML files
   python3 -m http.server 8000
   # Open browser to http://localhost:8000/ua_agree.html
   ```

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
3. **Wrong IP in JavaScript**: Verify server IP in script_python.js

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