from datetime import datetime
from typing import Dict, List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from config import settings
from database import MetricRecord, PredictionRecord
from model.lstm_model import LSTMModel
from services.action_engine import ActionEngine
from services.cost_calculator import CostCalculator
from utils.simulate_data import simulator

lstm_model = LSTMModel()
action_engine = ActionEngine()
cost_calculator = CostCalculator()


def get_history_series(db: Session) -> Tuple[List[float], List[float], int]:
    """Return CPU/memory history and current instance count for predictions."""
    recent_records = (
        db.query(MetricRecord)
        .order_by(desc(MetricRecord.timestamp))
        .limit(settings.sequence_length)
        .all()
    )

    if len(recent_records) < settings.sequence_length:
        cpu_data = simulator.get_mock_cpu_data(settings.sequence_length)
        memory_data = simulator.get_mock_memory_data(settings.sequence_length)
        current_instances = 1
    else:
        cpu_data = [r.cpu_utilization for r in reversed(recent_records)]
        memory_data = [r.memory_utilization for r in reversed(recent_records)]
        current_instances = recent_records[0].instance_count or 1

    return cpu_data, memory_data, current_instances


def compute_prediction(
    db: Session,
    *,
    current_instances: int = None,
    save: bool = False,
) -> Dict:
    """Build a prediction payload shared by API routes."""
    cpu_data, memory_data, history_instances = get_history_series(db)
    instances = current_instances if current_instances is not None else history_instances

    predicted_cpu = lstm_model.predict(cpu_data, memory_data)
    predicted_memory = lstm_model.predict(memory_data)
    confidence = lstm_model.get_prediction_confidence(cpu_data)

    action_data = action_engine.get_action(
        predicted_cpu, predicted_memory, instances, confidence
    )

    current_cost = cost_calculator.calculate_current_cost(
        cpu_data[-1], memory_data[-1], instances
    )
    predicted_cost = cost_calculator.calculate_predicted_cost(
        predicted_cpu, predicted_memory, action_data["recommended_instances"]
    )

    if save:
        db.add(
            PredictionRecord(
                predicted_cpu=predicted_cpu,
                predicted_memory=predicted_memory,
                recommended_action=action_data["action"],
                confidence=confidence,
                cost_savings=action_data["cost_impact"]["potential_savings"],
            )
        )
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
        "cost_savings": round(action_data["cost_impact"]["potential_savings"], 4),
        "current_instances": instances,
    }
