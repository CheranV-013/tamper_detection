# AI-Powered Tamper Detection and Security Monitoring Dashboard

## Overview
Full-stack SOC-style dashboard with simulated logs, IoT sensor telemetry, Isolation Forest anomaly detection, and real-time WebSocket alerts. The system logs access metadata (IP, user agent, endpoint, location, risk score) and surfaces live access threat intelligence.

## Project Structure
- `backend/` Flask API + Socket.IO + ML pipeline
- `frontend/` React + Tailwind dashboard
- `database/` SQLite schema

## Backend Setup
```bash
cd /Users/cheranv/Documents/iot_tamper/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
The backend runs at `https://tamper-detection-2.onrender.com`.

## Frontend Setup
```bash
cd /Users/cheranv/Documents/iot_tamper/frontend
npm install
npm run dev
```

## Real-Time Flow
- WebSocket connects on page load
- Server broadcasts `security_event` and `user_count`
- Access metadata is logged on every request (except `/socket.io` transport)
- UI updates instantly, no manual refresh

## API
- `POST /api/generate` to simulate events
- `GET /api/summary`, `GET /api/logs`, `GET /api/iot`, `GET /api/anomalies`, `GET /api/alerts`
- `GET /api/access-logs`, `GET /api/charts/access-hour`, `GET /api/charts/access-top-ips`, `GET /api/charts/access-suspicious`, `GET /api/charts/access-locations`
- `GET /api/dashboard-access` to log dashboard access

## Database
SQLite file at `database/tamper.db` is created on first backend run.
