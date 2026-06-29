import random


def read_ec_sensor(batch_id: str):
    ec_value = round(random.uniform(0.1, 2.5), 2)
    tampered = False
    status = "PASS" if ec_value >= 0.5 and ec_value <= 2.0 else "FLAG"
    return {
        "batch_id": batch_id,
        "ec_value": ec_value,
        "tampered": tampered,
        "status": status,
    }
