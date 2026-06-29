@echo off
cd /d "C:\Users\kalla\farmchain"

set HARDHAT_PORT=8545
set API_PORT=8000

call :EnsurePortFree %HARDHAT_PORT% HARDHAT_FREE
if %HARDHAT_FREE%==1 (
    echo Starting Hardhat node...
    start "FarmChain Hardhat" cmd /c "start_hardhat.bat"
) else (
    echo Port %HARDHAT_PORT% is still busy, skipping Hardhat launch.
)

timeout /t 8 /nobreak >nul

call :EnsurePortFree %API_PORT% API_FREE
if %API_FREE%==1 (
    echo Starting FastAPI server...
    start "FarmChain API" cmd /c "start.bat"
) else (
    echo Port %API_PORT% is still busy, skipping API launch.
)

timeout /t 5 /nobreak >nul

echo Starting Electron app...
start "FarmChain App" cmd /c "npm run electron"

echo FarmChain app launch sequence started.
exit /b 0

:EnsurePortFree
setlocal
set PORT=%1
set SERVICE_FLAG=%2
call :GetPortPid %PORT% PID
if %PID%==0 (
    endlocal & set %SERVICE_FLAG%=1
    exit /b 0
)
echo Port %PORT% is in use by PID %PID%. Attempting to stop it...
taskkill /pid %PID% /f >nul 2>&1
if %errorlevel%==0 (
    echo Stopped PID %PID% successfully.
) else (
    echo Failed to stop PID %PID%. You may need to close it manually.
)
timeout /t 2 /nobreak >nul
call :IsPortInUse %PORT% STILL_IN_USE
if %STILL_IN_USE%==0 (
    endlocal & set %SERVICE_FLAG%=1
) else (
    endlocal & set %SERVICE_FLAG%=0
)
exit /b 0

:GetPortPid
setlocal
set PORT=%1
set PID=0
for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "try { $c = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($c) { Write-Output $c.OwningProcess } } catch { }"`) do set PID=%%A
if %PID%==0 (
    endlocal & set %2=0
) else (
    endlocal & set %2=%PID%
)
exit /b 0

:IsPortInUse
setlocal
set PORT=%1
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if %errorlevel%==0 (
    endlocal & set %2=1
) else (
    endlocal & set %2=0
)
exit /b 0
