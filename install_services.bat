@echo off
:: Check for Admin Privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting Admin Privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

:: --- MAIN SCRIPT ---
set "NSSM_EXE=%~dp0nssm.exe"
:: HARDCODED PATHS
set "PYTHON_EXE=C:\Python314\python.exe"
set "NPM_CMD=C:\Program Files\nodejs\npm.cmd"

if not exist "%NSSM_EXE%" (
    echo [ERROR] nssm.exe not found!
    pause
    exit
)

echo.
echo [INFO] Stopping potential conflicting processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo.
echo 1. Removing Old Services...
"%NSSM_EXE%" stop PlanningBackend >nul 2>&1
"%NSSM_EXE%" remove PlanningBackend confirm >nul 2>&1
"%NSSM_EXE%" stop PlanningFrontend >nul 2>&1
"%NSSM_EXE%" remove PlanningFrontend confirm >nul 2>&1

echo.
echo 2. Installing Backend Service...
:: Using -u for Unbuffered Output to capture errors
:: Using --reload is bad for prod usually, but okay for now. Better to remove it for stability? Keeping for consistency
"%NSSM_EXE%" install PlanningBackend "%PYTHON_EXE%" "-u -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
"%NSSM_EXE%" set PlanningBackend AppDirectory "%~dp0"
"%NSSM_EXE%" set PlanningBackend Start SERVICE_AUTO_START
"%NSSM_EXE%" set PlanningBackend AppStdout "%~dp0backend.log"
"%NSSM_EXE%" set PlanningBackend AppStderr "%~dp0backend_error.log"
"%NSSM_EXE%" start PlanningBackend

echo.
echo 3. Installing Frontend Service...
"%NSSM_EXE%" install PlanningFrontend "%NPM_CMD%" "start"
"%NSSM_EXE%" set PlanningFrontend AppDirectory "%~dp0frontend"
"%NSSM_EXE%" set PlanningFrontend Start SERVICE_AUTO_START
"%NSSM_EXE%" set PlanningFrontend AppStdout "%~dp0frontend.log"
"%NSSM_EXE%" set PlanningFrontend AppStderr "%~dp0frontend_error.log"
"%NSSM_EXE%" start PlanningFrontend

echo.
echo [SUCCESS] Services Re-Installed and Started!
echo Please wait 10 seconds for services to spin up.
echo Login: http://localhost:3000
pause
