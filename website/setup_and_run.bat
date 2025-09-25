@echo off
echo ================================
echo PDF Text Extractor Setup Script
echo ================================
echo.

echo Installing Backend Dependencies...
cd backend
call npm install
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo Installing Frontend Dependencies...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo Installing Python Dependencies...
cd ..\..\text-extractor
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo ================================
echo Setup Complete! Starting servers...
echo ================================
echo.

cd ..\website

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && npm start"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ================================
echo Servers are starting!
echo ================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul