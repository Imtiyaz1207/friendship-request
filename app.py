from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz
import requests
import os
import csv
from dotenv import load_dotenv

app = Flask(__name__)

# Load Google Script URL
load_dotenv()
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")

# Log file path
LOG_FILE = "logs.csv"

# Create CSV if not exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "event", "ip_address"])

# Indian timezone
india = pytz.timezone('Asia/Kolkata')

# ✅ Function to correctly get real IP address (even behind proxy)
def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        # Take the first IP in the forwarded list (actual client)
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    else:
        ip = request.remote_addr
    return ip

# ✅ Log function (same as before)
def log_event(event, ip):
    time_now = datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")

    # Write to CSV file
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([time_now, event, ip])

    # Send to Google Sheet (Apps Script)
    if GOOGLE_SCRIPT_URL:
        try:
            requests.post(GOOGLE_SCRIPT_URL, json={
                "time": time_now,
                "event": event,
                "ip_address": ip
            })
        except Exception as e:
            print("Google Sheet log failed:", e)

@app.route("/")
def index():
    ip = get_client_ip()     # ✅ fixed IP retrieval
    log_event("page_visit", ip)
    return render_template("index.html")

@app.route("/log_action", methods=["POST"])
def log_action():
    data = request.get_json()
    event = data.get("event", "unknown")
    ip = get_client_ip()     # ✅ fixed IP retrieval
    log_event(event, ip)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
