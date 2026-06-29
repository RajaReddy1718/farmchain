from fastapi import APIRouter
from database import get_conn, init_db
from blockchain import PRIVATE_KEY, record_sensor_reading_on_chain
from sensor.simulator import read_ec_sensor

router = APIRouter()


@router.post("/record/{batch_id}")
def record_sensor(batch_id: str):
    init_db()
    reading = read_ec_sensor(batch_id)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sensor_readings(batch_id, ec_value, tampered, status) VALUES (?,?,?,?)",
            (batch_id, reading["ec_value"], int(reading["tampered"]), reading["status"]),
        )

    try:
        blockchain_result = record_sensor_reading_on_chain(
            batch_id,
            int(round(reading["ec_value"] * 100)),
            reading["tampered"],
            PRIVATE_KEY,
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        blockchain_result = {"status": "error", "error": str(exc)}

    reading["blockchain"] = blockchain_result
    return reading
