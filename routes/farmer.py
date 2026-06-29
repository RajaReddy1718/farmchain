from fastapi import APIRouter, Depends
from models import FarmerRegister
from blockchain import register_farmer_on_chain, PRIVATE_KEY
from database import get_conn
from auth import require_api_key

router = APIRouter()

@router.post("/register", dependencies=[Depends(require_api_key)])
def register_farmer(farmer: FarmerRegister):
    with get_conn() as conn:
        if conn.execute("SELECT 1 FROM farmers WHERE wallet_address=?", (farmer.wallet_address,)).fetchone():
            return {"error": "Farmer already registered"}
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
