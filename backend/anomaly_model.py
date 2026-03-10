from datetime import datetime, timedelta
import ipaddress
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
def detect_anomalies(data):
    from sklearn.ensemble import IsolationForest

UNUSUAL_HOURS = set([0, 1, 2, 3, 4, 5])


def _parse_ts(df):
    return pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")


def _log_features(logs_df):
    df = logs_df.copy()
    df["ts"] = _parse_ts(df)
    df["login_hour"] = df["ts"].dt.hour.fillna(0).astype(int)
    df["failed_attempt"] = (df["status"] == "failed").astype(int)
    df["unauthorized_access"] = (
        (df["action"] == "file_access")
        & (df["resource"] == "config.txt")
        & (df["status"] == "failed")
    ).astype(int)

    access_freq = []
    for idx, row in df.iterrows():
        if pd.isna(row["ts"]):
            access_freq.append(0)
            continue
        start = row["ts"] - timedelta(minutes=60)
        mask = (
            (df["user"] == row["user"])
            & (df["ts"] >= start)
            & (df["ts"] <= row["ts"])
        )
        access_freq.append(int(mask.sum()))
    df["access_frequency"] = access_freq

    features = df[[
        "login_hour",
        "failed_attempt",
        "access_frequency",
        "unauthorized_access",
    ]].fillna(0)
    return df, features


def _iot_features(iot_df):
    df = iot_df.copy()
    df["door_open"] = (df["door"] == "open").astype(int)
    features = df[[
        "temperature",
        "vibration",
        "motion",
        "door_open",
        "power",
        "tilt",
    ]].fillna(0)
    return df, features


def _log_rules(row):
    reasons = []
    if row["failed_attempt"] == 1:
        reasons.append("failed login")
    if row["login_hour"] in UNUSUAL_HOURS:
        reasons.append("unusual login hour")
    if row["unauthorized_access"] == 1:
        reasons.append("unauthorized file access")
    return reasons


def _iot_rules(row):
    reasons = []
    if row["vibration"] >= 2.0:
        reasons.append("high vibration")
    if row["door_open"] == 1:
        reasons.append("door opened unexpectedly")
    if row["tilt"] >= 10:
        reasons.append("device tilt detected")
    if row["motion"] == 1:
        reasons.append("motion detected")
    return reasons


def detect_anomalies(conn, new_log_count=0, new_iot_count=0):
    events = []
    logs_df = pd.read_sql_query("SELECT * FROM logs", conn)
    iot_df = pd.read_sql_query("SELECT * FROM iot_data", conn)

    if not logs_df.empty:
        logs_df = logs_df.sort_values("timestamp")
    if not iot_df.empty:
        iot_df = iot_df.sort_values("timestamp")

    # Log anomaly model
    if len(logs_df) >= 20 and new_log_count > 0:
        log_df, log_features = _log_features(logs_df)
        log_model = IsolationForest(n_estimators=200, contamination=0.08, random_state=42)
        log_model.fit(log_features)

        recent = log_df.tail(new_log_count)
        recent_features = log_features.tail(new_log_count)
        scores = log_model.decision_function(recent_features)
        preds = log_model.predict(recent_features)

        for i, row in recent.iterrows():
            pos = recent.index.get_loc(i)
            anomaly_score = float(-scores[pos])
            is_anomaly = int(preds[pos]) == -1
            reasons = _log_rules(row)
            if is_anomaly or reasons:
                severity = "high" if is_anomaly and reasons else "medium" if is_anomaly else "low"
                description = (
                    f"Log anomaly: {', '.join(reasons)}" if reasons else "Log anomaly detected"
                )
                conn.execute(
                    "INSERT INTO anomalies (timestamp, source, severity, anomaly_score, description) VALUES (?, ?, ?, ?, ?)",
                    (row["timestamp"], "log", severity, anomaly_score, description),
                )
                if severity in ("high", "medium"):
                    conn.execute(
                        "INSERT INTO alerts (timestamp, alert_message, status) VALUES (?, ?, ?)",
                        (
                            row["timestamp"],
                            f"Tamper Alert: {description}",
                            "active",
                        ),
                    )
                if is_anomaly:
                    events.append(
                        {
                            "type": "AI_ANOMALY",
                            "message": "AI detected abnormal log activity",
                            "severity": "high",
                            "timestamp": row["timestamp"],
                        }
                    )
                if reasons:
                    events.append(
                        {
                            "type": "SUSPICIOUS_LOGIN",
                            "message": description,
                            "severity": "medium",
                            "timestamp": row["timestamp"],
                        }
                    )

    # IoT anomaly model
    if len(iot_df) >= 20 and new_iot_count > 0:
        iot_df2, iot_features = _iot_features(iot_df)
        iot_model = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
        iot_model.fit(iot_features)

        recent = iot_df2.tail(new_iot_count)
        recent_features = iot_features.tail(new_iot_count)
        scores = iot_model.decision_function(recent_features)
        preds = iot_model.predict(recent_features)

        for i, row in recent.iterrows():
            pos = recent.index.get_loc(i)
            anomaly_score = float(-scores[pos])
            is_anomaly = int(preds[pos]) == -1
            reasons = _iot_rules(row)
            if is_anomaly or reasons:
                severity = "high" if is_anomaly and reasons else "medium" if is_anomaly else "low"
                description = (
                    f"Sensor anomaly: {', '.join(reasons)}" if reasons else "Sensor anomaly detected"
                )
                conn.execute(
                    "INSERT INTO anomalies (timestamp, source, severity, anomaly_score, description) VALUES (?, ?, ?, ?, ?)",
                    (row["timestamp"], "iot", severity, anomaly_score, description),
                )
                if severity in ("high", "medium"):
                    conn.execute(
                        "INSERT INTO alerts (timestamp, alert_message, status) VALUES (?, ?, ?)",
                        (
                            row["timestamp"],
                            f"Tamper Alert: {description} on {row['device_id']}",
                            "active",
                        ),
                    )
                if is_anomaly:
                    events.append(
                        {
                            "type": "AI_ANOMALY",
                            "message": "AI detected abnormal IoT activity",
                            "severity": "high",
                            "timestamp": row["timestamp"],
                        }
                    )
                if reasons:
                    events.append(
                        {
                            "type": "IOT_TAMPER",
                            "message": f"Tamper detected on {row['device_id']}: {', '.join(reasons)}",
                            "severity": "critical",
                            "timestamp": row["timestamp"],
                        }
                    )
    return events


def _access_features(access_df):
    df = access_df.copy()
    df["ts"] = _parse_ts(df)
    df["access_hour"] = df["ts"].dt.hour.fillna(0).astype(int)

    req_5m = []
    req_60m = []
    is_public = []
    for _, row in df.iterrows():
        if pd.isna(row["ts"]):
            req_5m.append(0)
            req_60m.append(0)
            is_public.append(0)
            continue
        start_5 = row["ts"] - timedelta(minutes=5)
        start_60 = row["ts"] - timedelta(minutes=60)
        mask_ip = df["ip_address"] == row["ip_address"]
        req_5m.append(int(((df["ts"] >= start_5) & (df["ts"] <= row["ts"]) & mask_ip).sum()))
        req_60m.append(int(((df["ts"] >= start_60) & (df["ts"] <= row["ts"]) & mask_ip).sum()))
        try:
            is_public.append(0 if ipaddress.ip_address(row["ip_address"]).is_private else 1)
        except ValueError:
            is_public.append(1)

    df["requests_5m"] = req_5m
    df["requests_60m"] = req_60m
    df["is_public_ip"] = is_public
    features = df[[
        "access_hour",
        "requests_5m",
        "requests_60m",
        "is_public_ip",
        "risk_score",
    ]].fillna(0)
    return df, features


def detect_access_anomalies(conn, new_access_count=0):
    events = []
    access_df = pd.read_sql_query("SELECT * FROM access_logs", conn)
    if access_df.empty or new_access_count <= 0:
        return events

    access_df = access_df.sort_values("timestamp")
    if len(access_df) < 20:
        return events

    df, features = _access_features(access_df)
    model = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
    model.fit(features)

    recent = df.tail(new_access_count)
    recent_features = features.tail(new_access_count)
    scores = model.decision_function(recent_features)
    preds = model.predict(recent_features)

    for i, row in recent.iterrows():
        pos = recent.index.get_loc(i)
        anomaly_score = float(-scores[pos])
        is_anomaly = int(preds[pos]) == -1
        if is_anomaly or row["risk_score"] >= 70:
            conn.execute(
                "INSERT INTO anomalies (timestamp, source, severity, anomaly_score, description) VALUES (?, ?, ?, ?, ?)",
                (
                    row["timestamp"],
                    "access",
                    "high" if is_anomaly else "medium",
                    anomaly_score,
                    "Suspicious access pattern detected",
                ),
            )
            conn.execute(
                "INSERT INTO alerts (timestamp, alert_message, status) VALUES (?, ?, ?)",
                (
                    row["timestamp"],
                    f"Suspicious access detected from {row['ip_address']}",
                    "active",
                ),
            )
            events.append(
                {
                    "type": "SUSPICIOUS_ACCESS",
                    "message": "Suspicious access detected",
                    "severity": "high",
                    "timestamp": row["timestamp"],
                    "ip": row["ip_address"],
                    "endpoint": row["endpoint"],
                    "device": row["user_agent"],
                    "location": row["location"],
                    "risk_score": row["risk_score"],
                }
            )
    return events
