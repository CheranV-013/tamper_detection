import random
from datetime import datetime, timedelta

USERS = ["admin", "guest", "operator", "service", "analyst"]
ACTIONS = ["login", "file_access", "config_change", "backup", "logout"]
RESOURCES = ["system", "config.txt", "secrets.env", "firmware.bin", "db.sqlite"]
STATUS = ["success", "failed"]


def _random_ip():
    return f"192.168.1.{random.randint(2, 254)}"


def generate_logs(n=20, start_time=None):
    now = datetime.utcnow() if start_time is None else start_time
    logs = []
    for i in range(n):
        ts = now - timedelta(minutes=random.randint(0, 120))
        user = random.choice(USERS)
        action = random.choice(ACTIONS)
        resource = random.choice(RESOURCES)
        status = random.choices(STATUS, weights=[0.85, 0.15])[0]

        # tamper-like patterns
        if random.random() < 0.08:
            user = "admin"
            action = "login"
            status = "failed"
            ts = ts.replace(hour=random.choice([1, 2, 3, 4]))
        if random.random() < 0.05:
            user = "guest"
            action = "file_access"
            resource = "config.txt"
            status = "failed"

        logs.append(
            {
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "user": user,
                "action": action,
                "resource": resource,
                "status": status,
                "ip_address": _random_ip(),
            }
        )
    return logs
