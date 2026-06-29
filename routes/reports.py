from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from database import get_conn
from blockchain import PRIVATE_KEY, suspend_batch_on_chain, is_batch_suspended_on_chain

router = APIRouter()


class FraudReportRequest(BaseModel):
    consumer_id: Optional[str] = None
    reason: str


def should_auto_suspend(report_count: int) -> bool:
    return report_count >= 5


@router.post("/report/{batch_id}")
def report_batch(batch_id: str, payload: FraudReportRequest):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO fraud_reports(batch_id, consumer_id, reason) VALUES (?,?,?)",
            (batch_id, payload.consumer_id, payload.reason),
        )
        count = conn.execute(
            "SELECT COUNT(*) AS total FROM fraud_reports WHERE batch_id=?",
            (batch_id,),
        ).fetchone()["total"]

    suspended = False
    if should_auto_suspend(count):
        try:
            suspend_result = suspend_batch_on_chain(batch_id, PRIVATE_KEY)
            suspended = True
        except Exception as exc:  # pragma: no cover - defensive fallback
            suspend_result = {"status": "error", "error": str(exc)}
    else:
        suspend_result = {"status": "pending"}

    with get_conn() as conn:
        conn.execute(
            "UPDATE batches SET suspended=1 WHERE batch_id=? AND suspended=0",
            (batch_id,),
        )

    return {
        "status": "reported",
        "batch_id": batch_id,
        "report_count": count,
        "auto_suspended": suspended,
        "blockchain": suspend_result,
    }
