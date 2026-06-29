from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FarmerRegister(BaseModel):
    name: str
    farm_name: str
    location: str
    certification: str  # e.g. "USDA Organic"
    wallet_address: str

class BatchCreate(BaseModel):
    batch_id: str
    farmer_wallet: str
    crop_name: str
    harvest_date: str
    is_organic: bool
    quantity_kg: float
    notes: Optional[str] = ""

class TransportUpdate(BaseModel):
    batch_id: str
    handler: str          # "processor" | "transport" | "retailer"
    location: str
    tamper_detected: bool
    timestamp: Optional[str] = None

class BatchVerify(BaseModel):
    batch_id: str