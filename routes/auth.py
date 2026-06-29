from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth import get_api_key, verify_credentials

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    api_key: str

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if not verify_credentials(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"api_key": get_api_key()}
