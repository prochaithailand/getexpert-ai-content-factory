# line_webhook.py
# Temporary LINE webhook debug server to capture and log sender userId.
import http.server
import json
import os
import sys

PORT = 8000
LOG_FILE = "/app/logs/line_webhook.log"

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/webhook":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                events = payload.get("events", [])
                
                os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
                
                with open(LOG_FILE, "a", encoding="utf-8") as log_f:
                    for event in events:
                        source = event.get("source", {})
                        user_id = source.get("userId", "N/A")
                        timestamp = event.get("timestamp", "N/A")
                        message = event.get("message", {})
                        msg_type = message.get("type", "N/A")
                        
                        # Log ONLY userId, timestamp, and message type. No message text.
                        log_line = f"Timestamp: {timestamp} | Type: {msg_type} | UserID: {user_id}\n"
                        log_f.write(log_line)
                        print(log_line.strip())
                        
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'{{"error":"{str(e)}"}}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run():
    # Bind to 0.0.0.0 so Nginx or host can access it inside Docker
    server_address = ('0.0.0.0', PORT)
    httpd = http.server.HTTPServer(server_address, WebhookHandler)
    print(f"Starting LINE Webhook server on port {PORT}...")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == "__main__":
    run()
