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

    # Check if script.js is configured for localhost (should auto-detect now)
    with open('script.js', 'r') as f:
        content = f.read()
        if 'isLocal' not in content:
            print("\n⚠️  WARNING: script.js doesn't have auto-detection!")
            print("Please ensure you're using the updated script.js with environment detection")
        else:
            print("✅ script.js has auto-detection enabled")

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
        print("✅ Clean shutdown completed")


if __name__ == '__main__':
    main()
