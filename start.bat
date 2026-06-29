@echo off
cd /d "C:\Users\kalla\farmchain"
set API_PORT=8000

powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %API_PORT% -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if %errorlevel%==0 (
    echo Port %API_PORT% is already in use. FastAPI server will not start.
    exit /b 0
)

"C:\Users\kalla\anaconda3\Scripts\uvicorn.exe" main:app --host 0.0.0.0 --port %API_PORT%
