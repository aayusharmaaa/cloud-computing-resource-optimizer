from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import PredictionResponse, ActionResponse
from services.prediction_service import compute_prediction

router = APIRouter(prefix="/api/predict", tags=["predictions"])


@router.get("/", response_model=PredictionResponse)
def get_prediction(db: Session = Depends(get_db)):
    """Get current prediction and recommendation."""
    return compute_prediction(db, save=True)


@router.get("/action", response_model=ActionResponse)
def get_action_recommendation(current_instances: int = 1, db: Session = Depends(get_db)):
    """Get detailed action recommendation for the requested instance count."""
    prediction = compute_prediction(db, current_instances=current_instances, save=False)
    action_data = prediction["action_details"]

    return {
        "action": action_data["action"],
        "current_instances": action_data["current_instances"],
        "recommended_instances": action_data["recommended_instances"],
        "reason": action_data["reason"],
        "urgency": action_data["urgency"],
        "cost_impact": action_data["cost_impact"],
        "confidence": action_data["confidence"],
    }
