@echo off
echo Starting AgentMonitor Backend...
cd ..
call venv\Scripts\activate.bat
cd backend
python app.py
