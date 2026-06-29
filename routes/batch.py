from fastapi import APIRouter, Depends
from models import BatchCreate, TransportUpdate
from qr_generator import generate_qr
from blockchain import register_batch_on_chain, add_handler_on_chain, PRIVATE_KEY
from database import get_conn
from auth import require_api_key
import os
from dotenv import load_dotenv

load_dotenv()
VERIFY_BASE_URL = os.getenv("VERIFY_BASE_URL", "http://localhost:8000/verify")

router = APIRouter()

def _build_verify_url(batch_id: str) -> str:
    base = VERIFY_BASE_URL.rstrip('/')
    if not base.endswith('/verify'):
        base += '/verify'
    return f"{base}/{batch_id}"

@router.post("/register", dependencies=[Depends(require_api_key)])
def register_batch(batch: BatchCreate):
    with get_conn() as conn:
        if conn.execute("SELECT 1 FROM batches WHERE batch_id=?", (batch.batch_id,)).fetchone():
            return {"error": "Batch ID already exists"}
        conn.execute(
            "INSERT INTO batches(batch_id,farmer_wallet,crop_name,harvest_date,is_organic,quantity_kg,notes) VALUES(?,?,?,?,?,?,?)",
            (batch.batch_id, batch.farmer_wallet, batch.crop_name, batch.harvest_date,
             int(batch.is_organic), batch.quantity_kg, batch.notes)
        )
    verify_url = _build_verify_url(batch.batch_id)
    qr_path = generate_qr(batch.batch_id, verify_url)
    chain_result = register_batch_on_chain(
        batch.batch_id, batch.crop_name, batch.harvest_date,
        batch.is_organic, batch.quantity_kg, PRIVATE_KEY
    )
    return {
        "status": "registered",
        "batch_id": batch.batch_id,
        "qr_code": qr_path,
        "verify_url": verify_url,
        "blockchain": chain_result
    }

@router.post("/update-transport", dependencies=[Depends(require_api_key)])
def update_transport(update: TransportUpdate):
    with get_conn() as conn:
        if not conn.execute("SELECT 1 FROM batches WHERE batch_id=?", (update.batch_id,)).fetchone():
            return {"error": "Batch not found"}
        conn.execute(
            "INSERT INTO handlers(batch_id,handler,location,tamper,timestamp) VALUES(?,?,?,?,?)",
            (update.batch_id, update.handler, update.location, int(update.tamper_detected), update.timestamp)
        )
        if update.tamper_detected:
            conn.execute("UPDATE batches SET tamper_detected=1 WHERE batch_id=?", (update.batch_id,))
    handler_info = f"{update.handler}|{update.location}|{update.timestamp}"
    chain_result = add_handler_on_chain(update.batch_id, handler_info, update.tamper_detected, PRIVATE_KEY)
    return {"status": "updated", "batch_id": update.batch_id, "blockchain": chain_result}

@router.get("/{batch_id}")
def get_batch(batch_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM batches WHERE batch_id=?", (batch_id,)).fetchone()
        if not row:
            return {"error": "Batch not found"}
        handlers = conn.execute(
            "SELECT handler,location,tamper,timestamp FROM handlers WHERE batch_id=?", (batch_id,)
        ).fetchall()
    b = dict(row)
    b["is_organic"] = bool(b["is_organic"])
    b["tamper_detected"] = bool(b["tamper_detected"])
    b["handlers"] = [{**dict(h), "tamper": bool(h["tamper"])} for h in handlers]
    return b
