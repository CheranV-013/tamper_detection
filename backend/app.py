import eventlet
eventlet.monkey_patch()

import ipaddress
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

from backend.database import init_db, get_conn
from backend.log_generator import generate_logs
from backend.iot_simulator import generate_iot_events
from backend.anomaly_model import detect_anomalies, detect_access_anomalies, UNUSUAL_HOURS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

init_db()
@app.route("/")
def home():
    return {"message": "AI IoT Tamper Detection API is running"}

connected_users = 0


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


def get_client_ip():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip or "unknown"


def approximate_location(ip):
    try:
        if ipaddress.ip_address(ip).is_private:
            return "Local Network"
        return "Unknown (Public)"
    except ValueError:
        return "Unknown"


def compute_risk_score(conn, ip, user_agent, endpoint, now_ts):

    score = 10

    if endpoint == "/api/dashboard-access":
        score += 20

    if now_ts.hour in UNUSUAL_HOURS:
        score += 20

    ua = (user_agent or "").lower()

    if any(x in ua for x in ["bot", "curl", "python", "wget"]):
        score += 25

    try:
        if not ipaddress.ip_address(ip).is_private:
            score += 10
    except:
        score += 10

    start_5 = (now_ts - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

    req_5 = conn.execute(
        "SELECT COUNT(*) as c FROM access_logs WHERE ip_address=? AND timestamp >= ?",
        (ip, start_5),
    ).fetchone()["c"]

    score += min(req_5 * 5, 25)

    return max(0, min(100, score))


@app.before_request
def log_access():

    if request.path.startswith("/socket.io"):
        return

    now_ts = datetime.utcnow()

    ip = get_client_ip()

    ua = request.headers.get("User-Agent", "unknown")

    endpoint = request.path

    location = approximate_location(ip)

    with get_conn() as conn:

        risk_score = compute_risk_score(conn, ip, ua, endpoint, now_ts)

        conn.execute(
            """
            INSERT INTO access_logs
            (timestamp, ip_address, user_agent, endpoint, risk_score, location)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                now_ts.strftime("%Y-%m-%d %H:%M:%S"),
                ip,
                ua,
                endpoint,
                risk_score,
                location,
            ),
        )

        access_events = detect_access_anomalies(conn, new_access_count=1)

    socketio.emit(
        "access_event",
        {
            "timestamp": now_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ip,
            "endpoint": endpoint,
            "risk": risk_score,
            "location": location,
        },
    )

    socketio.emit(
        "security_event",
        {
            "type": "ACCESS_DETECTED",
            "message": f"Endpoint accessed: {endpoint}",
            "severity": "warning",
            "timestamp": now_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ip,
            "endpoint": endpoint,
            "device": ua,
            "location": location,
            "risk_score": risk_score,
        },
    )

    for ev in access_events:
        socketio.emit("security_event", ev)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@socketio.on("connect")
def handle_connect():

    global connected_users
    connected_users += 1

    socketio.emit(
        "security_event",
        {
            "type": "ACCESS",
            "message": "User connected to SOC dashboard",
            "severity": "info",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

    socketio.emit("user_count", {"count": connected_users})


@socketio.on("disconnect")
def handle_disconnect():

    global connected_users
    connected_users = max(0, connected_users - 1)

    socketio.emit("user_count", {"count": connected_users})


@app.route("/api/summary")
def summary():

    with get_conn() as conn:

        total_logs = conn.execute("SELECT COUNT(*) as c FROM logs").fetchone()["c"]
        total_iot = conn.execute("SELECT COUNT(*) as c FROM iot_data").fetchone()["c"]
        total_anom = conn.execute("SELECT COUNT(*) as c FROM anomalies").fetchone()["c"]

        active_alerts = conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE status='active'"
        ).fetchone()["c"]

        access_total = conn.execute(
            "SELECT COUNT(*) as c FROM access_logs"
        ).fetchone()["c"]

    return jsonify(
        {
            "total_logs": total_logs,
            "total_iot": total_iot,
            "anomalies": total_anom,
            "active_alerts": active_alerts,
            "connected_users": connected_users,
            "access_total": access_total,
        }
    )


@app.route("/api/logs")
def logs():

    limit = int(request.args.get("limit", 20))

    with get_conn() as conn:

        rows = conn.execute(
            "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/iot")
def iot():

    limit = int(request.args.get("limit", 20))

    with get_conn() as conn:

        rows = conn.execute(
            "SELECT * FROM iot_data ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/anomalies")
def anomalies():

    limit = int(request.args.get("limit", 20))

    with get_conn() as conn:

        rows = conn.execute(
            "SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/alerts")
def alerts():

    limit = int(request.args.get("limit", 10))

    with get_conn() as conn:

        rows = conn.execute(
            "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/access-logs")
def access_logs():

    limit = int(request.args.get("limit", 20))

    with get_conn() as conn:

        rows = conn.execute(
            "SELECT * FROM access_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/charts/activity")
def activity_chart():

    with get_conn() as conn:

        rows = conn.execute(
            """
            SELECT substr(timestamp,1,13) as hour, COUNT(*) as count
            FROM logs
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 12
            """
        ).fetchall()

    data = [{"hour": r["hour"], "count": r["count"]} for r in rows]

    data.reverse()

    return jsonify(data)


@app.route("/api/charts/iot")
def iot_chart():

    with get_conn() as conn:

        rows = conn.execute(
            """
            SELECT substr(timestamp,1,13) as hour,
            AVG(temperature) as temperature,
            AVG(vibration) as vibration,
            AVG(power) as power
            FROM iot_data
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 12
            """
        ).fetchall()

    data = [
        {
            "hour": r["hour"],
            "temperature": round(r["temperature"] or 0, 2),
            "vibration": round(r["vibration"] or 0, 2),
            "power": round(r["power"] or 0, 2),
        }
        for r in rows
    ]

    data.reverse()

    return jsonify(data)


@app.route("/api/charts/tamper")
def tamper_chart():

    with get_conn() as conn:

        log_anom = conn.execute(
            "SELECT COUNT(*) as c FROM anomalies WHERE source='log'"
        ).fetchone()["c"]

        iot_anom = conn.execute(
            "SELECT COUNT(*) as c FROM anomalies WHERE source='iot'"
        ).fetchone()["c"]

        file_anom = conn.execute(
            "SELECT COUNT(*) as c FROM anomalies WHERE description LIKE '%file%'"
        ).fetchone()["c"]

    return jsonify(
        [
            {"name": "Login", "count": log_anom},
            {"name": "Sensor", "count": iot_anom},
            {"name": "File Access", "count": file_anom},
        ]
    )


@app.route("/api/charts/access-hour")
def access_hour_chart():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT substr(timestamp,1,13) as hour, COUNT(*) as count
            FROM access_logs
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 12
            """
        ).fetchall()

    data = [{"hour": r["hour"], "count": r["count"]} for r in rows]
    data.reverse()
    return jsonify(data)


@app.route("/api/charts/access-top-ips")
def access_top_ips():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT ip_address as ip, COUNT(*) as count
            FROM access_logs
            GROUP BY ip_address
            ORDER BY count DESC
            LIMIT 6
            """
        ).fetchall()

    return jsonify([{"ip": r["ip"], "count": r["count"]} for r in rows])


@app.route("/api/charts/access-suspicious")
def access_suspicious():
    with get_conn() as conn:
        suspicious = conn.execute(
            "SELECT COUNT(*) as c FROM access_logs WHERE risk_score >= 70"
        ).fetchone()["c"]

        total = conn.execute(
            "SELECT COUNT(*) as c FROM access_logs"
        ).fetchone()["c"]

    return jsonify(
        [
            {"name": "Suspicious", "count": suspicious},
            {"name": "Normal", "count": max(0, total - suspicious)},
        ]
    )


@app.route("/api/charts/access-locations")
def access_locations():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT location as name, COUNT(*) as count
            FROM access_logs
            GROUP BY location
            ORDER BY count DESC
            LIMIT 6
            """
        ).fetchall()

    return jsonify([{"name": r["name"], "count": r["count"]} for r in rows])


@app.route("/api/system-status")
def system_status():

    with get_conn() as conn:

        alerts = conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE status='active'"
        ).fetchone()["c"]

    return jsonify(
        {
            "system_health": "degraded" if alerts > 0 else "optimal",
            "sensor_status": "monitoring",
            "network_activity": "normal" if alerts == 0 else "elevated",
        }
    )


@app.route("/api/generate", methods=["POST"])
def generate():

    payload = request.get_json(silent=True) or {}

    log_count = int(payload.get("logs", 20))
    iot_count = int(payload.get("iot", 20))

    logs = generate_logs(log_count)
    iot_rows = generate_iot_events(iot_count)

    with get_conn() as conn:

        conn.executemany(
            "INSERT INTO logs (timestamp, user, action, resource, status, ip_address) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    l["timestamp"],
                    l["user"],
                    l["action"],
                    l["resource"],
                    l["status"],
                    l["ip_address"],
                )
                for l in logs
            ],
        )

        conn.executemany(
            "INSERT INTO iot_data (timestamp, device_id, temperature, vibration, motion, door, power, tilt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    r["timestamp"],
                    r["device_id"],
                    r["temperature"],
                    r["vibration"],
                    r["motion"],
                    r["door"],
                    r["power"],
                    r["tilt"],
                )
                for r in iot_rows
            ],
        )

        events = detect_anomalies(conn, new_log_count=log_count, new_iot_count=iot_count)

    for ev in events:
        socketio.emit("security_event", ev)

    return jsonify({"logs": log_count, "iot": iot_count, "status": "generated"})


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
