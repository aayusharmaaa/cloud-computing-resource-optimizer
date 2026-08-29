from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import DashboardStats
from services.cost_calculator import CostCalculator
from services.prediction_service import compute_prediction
from utils.simulate_data import simulator

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

cost_calculator = CostCalculator()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics."""
    current_metrics = simulator.get_current_metrics()
    prediction = compute_prediction(db, save=False)

    current_cost = cost_calculator.calculate_current_cost(
        current_metrics["cpu"],
        current_metrics["memory"],
        prediction["current_instances"],
    )
    monthly_cost = cost_calculator.calculate_monthly_cost(current_cost)
    action_data = prediction["action_details"]

    return {
        "current_cpu": round(current_metrics["cpu"], 2),
        "current_memory": round(current_metrics["memory"], 2),
        "current_network": round(current_metrics["network"], 2),
        "predicted_cpu": prediction["predicted_cpu"],
        "predicted_memory": prediction["predicted_memory"],
        "recommended_action": prediction["recommended_action"],
        "current_cost_per_hour": round(current_cost, 4),
        "monthly_cost": round(monthly_cost, 2),
        "potential_savings": round(action_data["cost_impact"]["potential_savings"], 4),
        "savings_percentage": round(action_data["cost_impact"]["savings_percentage"], 2),
    }
