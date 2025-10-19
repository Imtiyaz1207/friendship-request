from flask import Flask, render_template, request
import csv
from datetime import datetime
import os
import requests  # for sending POST to Google Sheets
from dotenv import load_dotenv

# -------------------------------
# Load environment variables from .env
# -------------------------------
load_dotenv()  # Reads variables from .env
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")

if not GOOGLE_SCRIPT_URL:
    raise ValueError("❌ GOOGLE_SCRIPT_URL not found in .env")

# -------------------------------
# Create Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Local CSV log file
# -------------------------------
log_file = 'logs.csv'
if not os.path.exists(log_file):
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Action'])

# -------------------------------
# Home page
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------------
# Log endpoint
# -------------------------------
@app.route('/log', methods=['POST'])
def log_tap():
    data = request.json or {}
    action = data.get('action', 'tap')

    # Log locally
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), action])

    # Log to Google Sheet
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json={'action': action})
        print("Google Script response:", response.status_code, response.text)
        if response.status_code != 200:
            print("Error sending to Google Sheet:", response.text)
    except Exception as e:
        print(f"Exception sending to Google Sheet: {e}")

    return {'status': 'logged'}

# -------------------------------
# Run Flask app
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
