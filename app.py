from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
import csv
import threading
import time

app = Flask(__name__)

# Load environment variables (Google Script URL + RENDER URL)
load_dotenv()
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
RENDER_URL = os.getenv("RENDER_URL")  # your Render app URL (https://your-app.onrender.com)

# Absolute path for CSV log
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs.csv")

# Create CSV file if not exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "event", "ip_address"])

# Log event function (CSV + Google Sheet)
def log_event(event, ip):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Full timestamp

    # Write to local CSV
    try:
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([time_now, event, ip])
        print(f"Logged to CSV: {time_now} | {event} | {ip}")
    except Exception as e:
        print("CSV log failed:", e)

    # Send to Google Sheet
    try:
        if GOOGLE_SCRIPT_URL:
            response = requests.post(GOOGLE_SCRIPT_URL, json={
                "time": time_now,
                "event": event,
                "ip_address": ip
            })
            print("Google Sheet response:", response.text)
    except Exception as e:
        print("Google Sheet log failed:", e)


# -----------------------
# 🕒 Auto Keep-Alive Thread
# -----------------------
def keep_alive():
    """Ping Render URL every 10 minutes to prevent sleeping."""
    while True:
        try:
            if RENDER_URL:
                response = requests.get(RENDER_URL)
                print(f"[Keep-Alive] Pinged {RENDER_URL} | Status: {response.status_code}")
        except Exception as e:
            print("[Keep-Alive] Failed to ping:", e)
        time.sleep(600)  # 10 minutes


# Homepage
@app.route("/")
def index():
    ip = request.remote_addr
    log_event("page_visit", ip)
    return render_template("index.html")


# Log user actions
@app.route("/log_action", methods=["POST"])
def log_action():
    data = request.get_json()
    event = data.get("event", "unknown")
    ip = request.remote_addr
    log_event(event, ip)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Start keep-alive thread in background
    threading.Thread(target=keep_alive, daemon=True).start()

    # Run Flask app
    app.run(debug=True)
