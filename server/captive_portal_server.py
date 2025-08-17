#!/usr/bin/env python3
"""
Captive Portal Server for Zyxel USG Flex 200
Handles email collection from guest Wi-Fi users
"""

import os
import sys
import json
import csv
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Configuration
PORT = 8080
CSV_FILE_PATH = r'C:\export\export.csv'  # Windows path
# For testing on different systems
if sys.platform == 'darwin':  # macOS
    CSV_FILE_PATH = './export/export.csv'
elif sys.platform == 'linux':
    CSV_FILE_PATH = './export/export.csv'

# Ensure export directory exists
os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)

# Thread-safe email counter
email_counts = {}
email_lock = threading.Lock()


class CaptivePortalHandler(BaseHTTPRequestHandler):
    """HTTP request handler for captive portal"""

    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests to /append endpoint"""
        if self.path == '/append':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)

                # Parse JSON data
                data = json.loads(post_data.decode('utf-8'))
                email = data.get('field1', '').strip()

                if not email:
                    self.send_error(400, 'Email address required')
                    return

                # Get current date and time
                now = datetime.now()
                date_str = now.strftime('%m/%d/%Y')
                time_str = now.strftime('%I:%M:%S %p')

                # Update visit count (thread-safe)
                with email_lock:
                    if email in email_counts:
                        email_counts[email] += 1
                    else:
                        email_counts[email] = 1
                    visit_count = email_counts[email]

                # Prepare CSV row
                row_data = {
                    'Email Address': email,
                    'Date': date_str,
                    'Timestamp': time_str,
                    'Number of Visits': visit_count
                }

                # Write to CSV file
                file_exists = os.path.isfile(CSV_FILE_PATH)

                with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Email Address', 'Date', 'Timestamp', 'Number of Visits']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Write header if file is new
                    if not file_exists:
                        writer.writeheader()

                    writer.writerow(row_data)

                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'Data appended successfully')

                # Log to console
                print(f"[{datetime.now()}] Email collected: {email} (Visit #{visit_count})")

            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON data')
            except Exception as e:
                print(f"Error processing request: {e}")
                self.send_error(500, f'Server error: {str(e)}')
        else:
            self.send_error(404, 'Not found')

    def do_GET(self):
        """Handle GET requests for testing"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            html = '''
            <html>
            <head><title>Captive Portal Server</title></head>
            <body>
                <h1>Captive Portal Server Running</h1>
                <p>Server is ready to accept email submissions at POST /append</p>
                <p>CSV file location: {}</p>
            </body>
            </html>
            '''.format(CSV_FILE_PATH)
            self.wfile.write(html.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            status = {
                'status': 'healthy',
                'port': PORT,
                'csv_path': CSV_FILE_PATH,
                'emails_collected': len(email_counts)
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_error(404, 'Not found')

    def log_message(self, format, *args):
        """Custom log format"""
        return


def load_existing_counts():
    """Load existing email counts from CSV file on startup"""
    global email_counts
    if os.path.isfile(CSV_FILE_PATH):
        try:
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    email = row.get('Email Address', '')
                    count = int(row.get('Number of Visits', 1))
                    if email:
                        email_counts[email] = max(email_counts.get(email, 0), count)
            print(f"Loaded {len(email_counts)} existing email records")
        except Exception as e:
            print(f"Warning: Could not load existing counts: {e}")


def run_server():
    """Start the HTTP server"""
    load_existing_counts()

    server_address = ('', PORT)
    httpd = HTTPServer(server_address, CaptivePortalHandler)

    print(f"Captive Portal Server starting on port {PORT}")
    print(f"CSV file will be saved to: {CSV_FILE_PATH}")
    print(f"Server ready at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        httpd.shutdown()


if __name__ == '__main__':
    # Allow port override from command line
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    run_server()
