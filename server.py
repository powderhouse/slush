from http.server import HTTPServer, BaseHTTPRequestHandler
import csv
import os
import urllib.parse
import html

PORT = 8000
CSV_FILE = "form_submissions.csv"
HTML_FILE = "form.html"
RESPONSE_FILE = "response.html"

class FormHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve HTML form from a file"""
        # Read HTML from file or use fallback if file doesn't exist
        with open(HTML_FILE, 'r') as f:
            html_content = f.read()
            self.wfile.write(html_content.encode())

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        

    def do_POST(self):
        """Handle form submission and save to CSV"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = urllib.parse.parse_qs(post_data)
        
        # Process form data (each value is a list, take the first item)
        processed_data = {k: v[0] for k, v in form_data.items()}
        
        # Get existing CSV columns or use form fields if file doesn't exist
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
            with open(CSV_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                fieldnames = next(reader)  # Get header row
        else:
            fieldnames = list(processed_data.keys())
        
        # Ensure all columns from the form are included
        for key in processed_data.keys():
            if key not in fieldnames:
                fieldnames.append(key)
        
        # Write to CSV file
        file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(processed_data)
        
        # Send response back to user
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        with open(RESPONSE_FILE, 'r') as f:
            response = f.read()
            self.wfile.write(response.encode())

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, FormHandler)
    print(f"Server running on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()