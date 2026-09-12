# DisasterGuard: Autonomous Basin Telemetry & Tactical Crisis Command Platform

> **Lead Architect & Developer:** Purbayan Pal  
> **Copyright:** (c) 2026 Purbayan Pal. All Rights Reserved.  
> **Mission:** Autonomous Flood Early Warning, Multi-Type GIS Intelligence, and Hardware Satellite GPS Distress Triage.

---

## Portals Included
1. **Admin Tactical Command Room (/)**:
   - Live Ticking IST Clock
   - Multi-Type GIS Map Engine (Satellite Aerial, High-Contrast Streets, River & Topo Terrain, Tactical Dark)
   - Dynamic Telemetry Indicators (GloFAS Streamflow, Precipitation Rate, Crest Lag, CWC Gauge Level)
   - Live River Hydrograph & Discharge Curve (Chart.js)
   - Precipitation Inundation Risk Chart (Chart.js)
   - Municipal Drainage Stress Bar Chart (Green / Yellow / Red Alerts)
   - Live SOS Distress Calls Triage & 2-Way Intercom

2. **Citizen Emergency Lifeline (/client)**:
   - Secure Phone + Password / Real GSM OTP Verification
   - Live Hardware Satellite GPS Pinning
   - Mobile Tactical GIS Map with Layer Switcher (Aerial, Streets, River/Topo, Dark)
   - Live Flood Threat Meter Gauge (Level 1 Safe / Level 2 Warning / Level 3 Breach)
   - Safe High-Ground Shelters Directory with 1-Tap Google Maps Navigation
   - Red Inundated Flood Zones & Safe High-Ground Corridors
   - Dual SOS: Instant Satellite SOS to Admin + 1-Tap WhatsApp/SMS to Relatives

---

## 1-Click Free Cloud Deployment (Render.com)
1. Push this folder to a new GitHub repository:
   `ash
   git init
   git add .
   git commit -m " DisasterGuard Complete Release\
 git branch -M main
 git remote add origin https://github.com/<YOUR-USERNAME>/disasterguard.git
 git push -u origin main
 `
2. Log into [Render.com](https://render.com) (Free Account).
3. Click **New +** -> **Web Service**.
4. Select your GitHub repository.
5. Set:
 - **Environment:** Python 3
 - **Build Command:** pip install -r requirements.txt
 - **Start Command:** uvicorn server:app --host 0.0.0.0 --port 
6. Click **Create Web Service**.
Your permanent 24/7 live URLs will be:
- Admin: https://disasterguard.onrender.com/
- Citizen: https://disasterguard.onrender.com/client

---

## Running Locally on Windows
Double-click START_DISASTERGUARD.bat or run:
`ash
.\\venv\\Scripts\\python.exe server.py
`
