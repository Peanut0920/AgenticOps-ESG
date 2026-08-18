@echo off
TITLE AgenticOps-ESG Launcher
ECHO 🚀 Launching AgenticOps-ESG...

REM Activate virtual environment and start backend
START "AgenticOps Backend" cmd /k ".venv\Scripts\activate && uvicorn backend_api.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait 2 seconds
timeout /t 2 /nobreak > nul

REM Start frontend in a new window
START "AgenticOps Frontend" cmd /k "cd frontend && python -m http.server 5500"

ECHO.
ECHO ✅ AgenticOps-ESG is starting!
ECHO    Backend:  http://localhost:8000/docs
ECHO    Frontend: http://localhost:5500
ECHO.
ECHO Press any key to close this launcher (the servers will keep running)...
pause > nul