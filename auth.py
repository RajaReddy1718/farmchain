import os
from typing import Optional
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()
_API_KEY = os.getenv("API_KEY", "")
_LOGIN_USERNAME = os.getenv("LOGIN_USERNAME", "admin")
_LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "password")

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not _API_KEY or x_api_key != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

def get_api_key() -> str:
    return _API_KEY

def verify_credentials(username: str, password: str) -> bool:
    return username == _LOGIN_USERNAME and password == _LOGIN_PASSWORD
