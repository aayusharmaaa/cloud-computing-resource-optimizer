from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, MetricRecord
from sqlalchemy import desc
from utils.simulate_data import simulator
from model.lstm_model import LSTMModel
from services.action_engine import ActionEngine
from services.cost_calculator import CostCalculator
from schemas import DashboardStats
from config import settings

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

lstm_model = LSTMModel()
action_engine = ActionEngine()
cost_calculator = CostCalculator()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    # Get current metrics
    current_metrics = simulator.get_current_metrics()
    
    # Get recent history for prediction
    recent_records = db.query(MetricRecord).order_by(desc(MetricRecord.timestamp)).limit(settings.sequence_length).all()
    
    if len(recent_records) < settings.sequence_length:
        cpu_data = simulator.get_mock_cpu_data(settings.sequence_length)
        memory_data = simulator.get_mock_memory_data(settings.sequence_length)
    else:
        cpu_data = [r.cpu_utilization for r in reversed(recent_records)]
        memory_data = [r.memory_utilization for r in reversed(recent_records)]
    
    # Make predictions
    predicted_cpu = lstm_model.predict(cpu_data)
    predicted_memory = lstm_model.predict(memory_data)
    confidence = lstm_model.get_prediction_confidence(cpu_data)
    
    # Get action recommendation
    current_instances = recent_records[0].instance_count if recent_records else 1
    action_data = action_engine.get_action(predicted_cpu, predicted_memory, current_instances, confidence)
    
    # Calculate costs
    current_cost = cost_calculator.calculate_current_cost(
        current_metrics["cpu"], current_metrics["memory"], current_instances
    )
    monthly_cost = cost_calculator.calculate_monthly_cost(current_cost)
    
    return {
        "current_cpu": round(current_metrics["cpu"], 2),
        "current_memory": round(current_metrics["memory"], 2),
        "current_network": round(current_metrics["network"], 2),
        "predicted_cpu": round(predicted_cpu, 2),
        "predicted_memory": round(predicted_memory, 2),
        "recommended_action": action_data["action"],
        "current_cost_per_hour": round(current_cost, 4),
        "monthly_cost": round(monthly_cost, 2),
        "potential_savings": round(action_data["cost_impact"]["potential_savings"], 4),
        "savings_percentage": round(action_data["cost_impact"]["savings_percentage"], 2)
    }


