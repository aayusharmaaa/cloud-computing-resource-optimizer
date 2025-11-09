from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, PredictionRecord, MetricRecord
from sqlalchemy import desc
from datetime import datetime
from utils.simulate_data import simulator
from model.lstm_model import LSTMModel
from services.action_engine import ActionEngine
from services.cost_calculator import CostCalculator
from schemas import PredictionResponse, ActionResponse
from config import settings

router = APIRouter(prefix="/api/predict", tags=["predictions"])

# Initialize services
lstm_model = LSTMModel()
action_engine = ActionEngine()
cost_calculator = CostCalculator()

@router.get("/", response_model=PredictionResponse)
def get_prediction(db: Session = Depends(get_db)):
    """Get current prediction and recommendation"""
    # Get recent CPU data
    recent_records = db.query(MetricRecord).order_by(desc(MetricRecord.timestamp)).limit(settings.sequence_length).all()
    
    if len(recent_records) < settings.sequence_length:
        # Not enough data, generate mock data
        cpu_data = simulator.get_mock_cpu_data(settings.sequence_length)
        memory_data = simulator.get_mock_memory_data(settings.sequence_length)
    else:
        cpu_data = [r.cpu_utilization for r in reversed(recent_records)]
        memory_data = [r.memory_utilization for r in reversed(recent_records)]
    
    # Make predictions
    predicted_cpu = lstm_model.predict(cpu_data)
    predicted_memory = lstm_model.predict(memory_data)
    confidence = lstm_model.get_prediction_confidence(cpu_data)
    
    # Get current instance count (default to 1)
    current_instances = recent_records[0].instance_count if recent_records else 1
    
    # Get action recommendation
    action_data = action_engine.get_action(predicted_cpu, predicted_memory, current_instances, confidence)
    
    # Calculate costs
    current_cost = cost_calculator.calculate_current_cost(
        cpu_data[-1], memory_data[-1], current_instances
    )
    predicted_cost = cost_calculator.calculate_predicted_cost(
        predicted_cpu, predicted_memory, action_data["recommended_instances"]
    )
    
    # Save prediction to database
    prediction_record = PredictionRecord(
        predicted_cpu=predicted_cpu,
        predicted_memory=predicted_memory,
        recommended_action=action_data["action"],
        confidence=confidence,
        cost_savings=action_data["cost_impact"]["potential_savings"]
    )
    db.add(prediction_record)
    db.commit()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_history": cpu_data,
        "memory_history": memory_data,
        "predicted_cpu": round(predicted_cpu, 2),
        "predicted_memory": round(predicted_memory, 2),
        "recommended_action": action_data["action"],
        "confidence": round(confidence, 2),
        "action_details": action_data,
        "current_cost": round(current_cost, 4),
        "predicted_cost": round(predicted_cost, 4),
        "cost_savings": round(action_data["cost_impact"]["potential_savings"], 4)
    }

@router.get("/action", response_model=ActionResponse)
def get_action_recommendation(current_instances: int = 1, db: Session = Depends(get_db)):
    """Get detailed action recommendation"""
    # Get prediction first
    prediction = get_prediction(db)
    
    action_data = action_engine.get_action(
        prediction["predicted_cpu"],
        prediction["predicted_memory"],
        current_instances,
        prediction["confidence"]
    )
    
    return {
        "action": action_data["action"],
        "current_instances": action_data["current_instances"],
        "recommended_instances": action_data["recommended_instances"],
        "reason": action_data["reason"],
        "urgency": action_data["urgency"],
        "cost_impact": action_data["cost_impact"],
        "confidence": action_data["confidence"]
    }

