import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from fastapi import APIRouter, Depends
from models import FarmerRegister
from blockchain import register_farmer_on_chain, PRIVATE_KEY
from database import get_conn
from auth import require_api_key

router = APIRouter()


def verify_usda_certificate(cert_number: str) -> bool:
    cert_number = (cert_number or "").strip()
    if not cert_number or cert_number.lower() in {"organic", "usda organic", "n/a", "none"}:
        return True

    url = f"https://api.ams.usda.gov/api/Organic/Certificate/{cert_number}"
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (URLError, HTTPError, ValueError, TimeoutError):
        return False

    status = str(data.get("status", "")).strip().lower()
    return status in {"active", "approved", "valid"}


@router.post("/register", dependencies=[Depends(require_api_key)])
def register_farmer(farmer: FarmerRegister):
    with get_conn() as conn:
        if conn.execute("SELECT 1 FROM farmers WHERE wallet_address=?", (farmer.wallet_address,)).fetchone():
            return {"error": "Farmer already registered"}

        cert_value = (farmer.certification or "").strip()
        if cert_value and cert_value.lower() not in {"organic", "usda organic", "n/a", "none"} and not verify_usda_certificate(cert_value):
            return {"error": "USDA certificate is invalid or inactive"}

        conn.execute(
            "INSERT INTO farmers(wallet_address,name,farm_name,location,certification) VALUES(?,?,?,?,?)",
            (farmer.wallet_address, farmer.name, farmer.farm_name, farmer.location, farmer.certification)
        )
    chain_result = register_farmer_on_chain(farmer.name, PRIVATE_KEY)
    return {
        "status": "registered",
        "farmer": farmer.name,
        "farm": farmer.farm_name,
        "certification": farmer.certification,
        "blockchain": chain_result
    }

@router.get("/{wallet_address}")
def get_farmer(wallet_address: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM farmers WHERE wallet_address=?", (wallet_address,)).fetchone()
    if not row:
        return {"error": "Farmer not found"}
    return dict(row)
