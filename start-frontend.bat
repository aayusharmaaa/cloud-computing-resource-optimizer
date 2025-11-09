@echo off
echo Starting Cloud Resource Optimizer Frontend...
cd frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start development server
echo Starting React development server on http://localhost:3000
npm start


