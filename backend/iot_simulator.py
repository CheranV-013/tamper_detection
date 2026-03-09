import random
from datetime import datetime, timedelta

DEVICES = ["device01", "device02", "device03"]


def generate_iot_events(n=20, start_time=None):
    now = datetime.utcnow() if start_time is None else start_time
    rows = []
    for _ in range(n):
        ts = now - timedelta(minutes=random.randint(0, 120))
        device_id = random.choice(DEVICES)
        temperature = round(random.uniform(20, 40), 1)
        vibration = round(random.uniform(0.0, 0.9), 2)
        motion = 1 if random.random() < 0.1 else 0
        door = "open" if random.random() < 0.05 else "closed"
        power = round(random.uniform(85, 100), 1)
        tilt = random.randint(0, 3) if random.random() < 0.05 else 0

        # tamper scenario
        if random.random() < 0.08:
            vibration = round(random.uniform(2.0, 3.5), 2)
            door = "open"
            tilt = random.randint(10, 20)
            motion = 1

        rows.append(
            {
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": device_id,
                "temperature": temperature,
                "vibration": vibration,
                "motion": motion,
                "door": door,
                "power": power,
                "tilt": tilt,
            }
        )
    return rows
