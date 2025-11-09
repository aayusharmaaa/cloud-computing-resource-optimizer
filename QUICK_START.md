# 🚀 Quick Start Guide - Preview the Application

## Step 1: Start the Backend Server

Open a terminal/PowerShell and run:

```bash
cd "cloud-resource-optimizer\backend"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

The backend will start at: **http://localhost:8000**
API docs available at: **http://localhost:8000/docs**

## Step 2: Start the Frontend (New Terminal)

Open a **new** terminal/PowerShell and run:

```bash
cd "cloud-resource-optimizer\frontend"

# Install dependencies (first time only)
npm install

# Start the development server
npm start
```

The frontend will automatically open at: **http://localhost:3000**

## What You'll See

### Dashboard Features:
1. **Metric Cards** - CPU and Memory utilization with trend indicators
2. **Cost Card** - Real-time cost analysis with savings potential
3. **Action Card** - AI recommendations with urgency badges
4. **Interactive Charts** - Multi-metric time-series visualization
5. **Real-Time Stream** - Live metrics updating every 2 seconds

### Interactive Elements:
- **🟢 Realtime Toggle** - Switch between live and manual modes
- **🔄 Refresh Button** - Manually fetch new predictions
- **Hover Effects** - Cards lift on hover
- **Chart Tooltips** - Detailed values on hover

## Preview Images Location

The actual running application will show:
- Beautiful gradient background
- Professional card-based layout
- Color-coded metrics (Red for CPU, Blue for Memory, Green for Network)
- Real-time data updates
- Cost savings calculations
- AI-powered recommendations

## Troubleshooting

### Backend Issues:
- Make sure Python 3.8+ is installed
- Check that port 8000 is not in use
- Verify dependencies are installed: `pip list`

### Frontend Issues:
- Make sure Node.js 14+ is installed
- Clear cache: `npm cache clean --force`
- Delete node_modules and reinstall if needed

### Connection Issues:
- Ensure backend is running before starting frontend
- Check browser console for errors
- Verify CORS settings if needed

## Alternative: Use Startup Scripts

### Windows:
- Backend: Double-click `start-backend.bat`
- Frontend: Double-click `start-frontend.bat`

### Linux/Mac:
- Backend: `./start-backend.sh`
- Frontend: `./start-frontend.sh`

Enjoy exploring your AI-Driven Cloud Resource Optimizer! 🎉


