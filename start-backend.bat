@echo off
echo Starting Cloud Resource Optimizer Backend...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create models directory
if not exist "models" mkdir models

REM Start server
echo Starting FastAPI server on http://localhost:8000
echo API documentation available at http://localhost:8000/docs
uvicorn main:app --reload --port 8000


