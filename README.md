# LocationTracker

It helps to find the exact location of a user (with their consent) by sending a link.  

**Author:** WEBXPLOIT  

---

## ⚠️ Warning
This tool is for **educational and ethical purposes only**.  
Do **not** use it to track users without their permission.

---

## Features
- Auto-play YouTube videos via a link.  
- Request user location in browser (lat, long).  
- Display visitor info: IP, coordinates, address, browser.  
- Save logs in `locations_log.txt`.  
- Share your local server using Cloudflare Tunnel.

---

## Requirements
- Python 3.8+  
- Flask  
- Requests  
- Colorama  
- Cloudflared

---

## Setup & Run
1. Install dependencies:
```bash
pip install flask requests colorama

2. Windows: Installing Cloudflared and Making it Globally Accessible
Download the Cloudflared .exe from Cloudflared Downloads (https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation)
Rename it to cloudflared.exe for convenience.
Move cloudflared.exe to: C:\Windows\System32
This makes it accessible from any Command Prompt.
Open a new Command Prompt and verify: cloudflared --version

## Run the script:
python location.py



