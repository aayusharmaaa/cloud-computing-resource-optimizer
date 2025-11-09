from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime

from config import settings
from database import init_db
from routers import metrics, predictions, dashboard
from utils.simulate_data import simulator
from services.cost_calculator import CostCalculator

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router)
app.include_router(predictions.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {
        "message": "Cloud Resource Optimizer API",
        "version": settings.api_version,
        "status": "operational",
        "endpoints": {
            "metrics": "/api/metrics",
            "predictions": "/api/predict",
            "dashboard": "/api/dashboard"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cost_calculator = CostCalculator()
    
    try:
        while True:
            # Get current metrics
            metrics = simulator.get_current_metrics()
            
            # Calculate cost
            current_cost = cost_calculator.calculate_current_cost(
                metrics["cpu"], metrics["memory"], 1
            )
            
            # Send data
            data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "cpu": round(metrics["cpu"], 2),
                "memory": round(metrics["memory"], 2),
                "network": round(metrics["network"], 2),
                "cost": round(current_cost, 4)
            }
            
            await websocket.send_json(data)
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()