@echo off
echo Starting SonicScribe...
call venv\Scripts\activate
uvicorn main:app --reload --port 8000
pause
