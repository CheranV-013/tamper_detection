import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

from database import init_db, get_conn
from log_generator import generate_logs
from iot_simulator import generate_iot_events
from anomaly_model import detect_anomalies

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

init_db()

connected_users = 0


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@socketio.on("connect")
def handle_connect():
    global connected_users
    connected_users += 1
    emit(
        "security_event",
        {
            "type": "ACCESS",
            "message": "New user connected to SOC dashboard",
            "severity": "medium",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        },
        broadcast=True,
    )
    emit("user_count", {"count": connected_users}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    global connected_users
    connected_users = max(0, connected_users - 1)
    emit("user_count", {"count": connected_users}, broadcast=True)


@app.route("/api/summary")
def summary():
    with get_conn() as conn:
        total_logs = conn.execute("SELECT COUNT(*) as c FROM logs").fetchone()["c"]
        total_iot = conn.execute("SELECT COUNT(*) as c FROM iot_data").fetchone()["c"]
        total_anomalies = conn.execute("SELECT COUNT(*) as c FROM anomalies").fetchone()["c"]
        active_alerts = conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE status='active'"
        ).fetchone()["c"]

    return jsonify(
        {
            "total_logs": total_logs,
            "total_iot": total_iot,
            "anomalies": total_anomalies,
            "active_alerts": active_alerts,
            "connected_users": connected_users,
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


@app.route("/api/charts/activity")
def activity_chart():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT substr(timestamp, 1, 13) as hour, COUNT(*) as count "
            "FROM logs GROUP BY hour ORDER BY hour DESC LIMIT 12"
        ).fetchall()
    data = [
        {"hour": r["hour"].replace(" ", "T") + ":00", "count": r["count"]}
        for r in rows
    ]
    data.reverse()
    return jsonify(data)


@app.route("/api/charts/iot")
def iot_chart():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT substr(timestamp, 1, 13) as hour, "
            "AVG(temperature) as temperature, AVG(vibration) as vibration, AVG(power) as power "
            "FROM iot_data GROUP BY hour ORDER BY hour DESC LIMIT 12"
        ).fetchall()
    data = [
        {
            "hour": r["hour"].replace(" ", "T") + ":00",
            "temperature": round(r["temperature"], 2) if r["temperature"] else 0,
            "vibration": round(r["vibration"], 2) if r["vibration"] else 0,
            "power": round(r["power"], 2) if r["power"] else 0,
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
            "SELECT COUNT(*) as c FROM anomalies WHERE description LIKE '%file%access%'"
        ).fetchone()["c"]
    return jsonify(
        [
            {"name": "Login", "count": log_anom},
            {"name": "Sensor", "count": iot_anom},
            {"name": "File Access", "count": file_anom},
        ]
    )


@app.route("/api/system-status")
def system_status():
    with get_conn() as conn:
        recent_alerts = conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE status='active'"
        ).fetchone()["c"]
    return jsonify(
        {
            "system_health": "degraded" if recent_alerts > 0 else "optimal",
            "sensor_status": "monitoring",
            "network_activity": "normal" if recent_alerts == 0 else "elevated",
        }
    )


@app.route("/api/dashboard-access")
def dashboard_access():
    socketio.emit(
        "security_event",
        {
            "type": "ACCESS",
            "message": "Dashboard accessed by user",
            "severity": "warning",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        },
        broadcast=True,
    )
    return jsonify({"status": "logged"})


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

    socketio.emit(
        "security_event",
        {
            "type": "LOG_CREATED",
            "message": f"{log_count} new logs ingested",
            "severity": "info",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        },
        broadcast=True,
    )
    socketio.emit(
        "security_event",
        {
            "type": "IOT_UPDATE",
            "message": f"{iot_count} new IoT events received",
            "severity": "info",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        },
        broadcast=True,
    )
    for ev in events:
        socketio.emit("security_event", ev, broadcast=True)

    return jsonify({"logs": log_count, "iot": iot_count, "status": "generated"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
