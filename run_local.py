#!/usr/bin/env python3
"""
Local development server for testing the captive portal
Runs both the API server and serves HTML files
"""

import os
import sys
import threading
import time
import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import signal

# Configuration
API_PORT = 8080
HTML_PORT = 8000

def run_api_server():
    """Run the Python API server"""
    print(f"Starting API server on port {API_PORT}...")
    subprocess.run([sys.executable, "server/captive_portal_server.py", str(API_PORT)])

def run_html_server():
    """Serve HTML files"""
    print(f"Starting HTML server on port {HTML_PORT}...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Expires', '0')
            super().end_headers()
    
    with HTTPServer(('', HTML_PORT), NoCacheHTTPRequestHandler) as httpd:
        httpd.serve_forever()

def signal_handler(sig, frame):
    print('\nShutting down servers...')
    sys.exit(0)

def main():
    print("=" * 50)
    print("Captive Portal Local Development Server")
    print("=" * 50)
    
    # Check if script_python.js is configured for localhost
    with open('script_python.js', 'r') as f:
        content = f.read()
        if '192.168.50.19' in content:
            print("\n⚠️  WARNING: script_python.js is configured for production!")
            print("The PYTHON_SERVER_URL is set to 192.168.50.19")
            response = input("Do you want to temporarily update it to localhost? (y/n): ")
            if response.lower() == 'y':
                # Backup original
                with open('script_python.js.backup', 'w') as backup:
                    backup.write(content)
                # Update to localhost
                new_content = content.replace('http://192.168.50.19:8080', 'http://localhost:8080')
                with open('script_python.js', 'w') as f:
                    f.write(new_content)
                print("✅ Updated to localhost (backup saved as script_python.js.backup)")
    
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start API server in a thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Give API server time to start
    time.sleep(2)
    
    # Start HTML server in a thread
    html_thread = threading.Thread(target=run_html_server, daemon=True)
    html_thread.start()
    
    # Give HTML server time to start
    time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🚀 Servers are running!")
    print("=" * 50)
    print(f"📄 HTML Server: http://localhost:{HTML_PORT}")
    print(f"🔧 API Server:  http://localhost:{API_PORT}")
    print(f"📧 Portal Page: http://localhost:{HTML_PORT}/ua_agree.html")
    print(f"📱 Mobile Page: http://localhost:{HTML_PORT}/ua_agree_m.html")
    print("\nPress Ctrl+C to stop all servers")
    print("=" * 50 + "\n")
    
    # Open browser
    webbrowser.open(f'http://localhost:{HTML_PORT}/ua_agree.html')
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        # Restore original script_python.js if backed up
        if os.path.exists('script_python.js.backup'):
            with open('script_python.js.backup', 'r') as backup:
                content = backup.read()
            with open('script_python.js', 'w') as f:
                f.write(content)
            os.remove('script_python.js.backup')
            print("✅ Restored original script_python.js")

if __name__ == '__main__':
    main()