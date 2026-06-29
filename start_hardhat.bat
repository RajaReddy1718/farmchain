@echo off
cd /d "C:\Users\kalla\farmchain"
set HARDHAT_PORT=8545

powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %HARDHAT_PORT% -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if %errorlevel%==0 (
    echo Port %HARDHAT_PORT% is already in use. Hardhat node will not start.
    exit /b 0
)

start /b "" "C:\Program Files\nodejs\node.exe" node_modules\hardhat\internal\cli\cli.js node > hardhat-node.log 2>&1
timeout /t 10 /nobreak >nul
"C:\Program Files\nodejs\node.exe" node_modules\hardhat\internal\cli\cli.js run scripts/deploy.js --network localhost >> hardhat-node.log 2>&1
