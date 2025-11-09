from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List
from database import get_db, MetricRecord, PredictionRecord
from utils.simulate_data import simulator
from schemas import MetricResponse, PredictionResponse

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/current", response_model=MetricResponse)
def get_current_metrics(db: Session = Depends(get_db)):
    """Get current real-time metrics"""
    from services.cost_calculator import CostCalculator
    
    metrics = simulator.get_current_metrics()
    cost_calc = CostCalculator()
    cost = cost_calc.calculate_current_cost(metrics["cpu"], metrics["memory"], 1)
    
    # Save to database
    record = MetricRecord(
        cpu_utilization=metrics["cpu"],
        memory_utilization=metrics["memory"],
        network_io=metrics["network"],
        cost=cost
    )
    db.add(record)
    db.commit()
    
    return {
        "timestamp": metrics["timestamp"],
        "cpu": metrics["cpu"],
        "memory": metrics["memory"],
        "network": metrics["network"],
        "cost": cost
    }

@router.get("/history", response_model=List[MetricResponse])
def get_metric_history(limit: int = 100, db: Session = Depends(get_db)):
    """Get historical metrics"""
    records = db.query(MetricRecord).order_by(desc(MetricRecord.timestamp)).limit(limit).all()
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "cpu": r.cpu_utilization,
            "memory": r.memory_utilization,
            "network": r.network_io,
            "cost": r.cost
        }
        for r in records
    ]

@router.get("/predictions", response_model=List[PredictionResponse])
def get_predictions(limit: int = 50, db: Session = Depends(get_db)):
    """Get prediction history"""
    records = db.query(PredictionRecord).order_by(desc(PredictionRecord.timestamp)).limit(limit).all()
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "predicted_cpu": r.predicted_cpu,
            "predicted_memory": r.predicted_memory,
            "recommended_action": r.recommended_action,
            "confidence": r.confidence,
            "cost_savings": r.cost_savings
        }
        for r in records
    ]

