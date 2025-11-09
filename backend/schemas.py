from pydantic import BaseModel
from typing import List, Optional

class MetricResponse(BaseModel):
    timestamp: Optional[str] = None
    cpu: float
    memory: float
    network: float
    cost: Optional[float] = 0.0

class PredictionResponse(BaseModel):
    timestamp: str
    cpu_history: List[float]
    memory_history: List[float]
    predicted_cpu: float
    predicted_memory: float
    recommended_action: str
    confidence: float
    action_details: dict
    current_cost: float
    predicted_cost: float
    cost_savings: float

class ActionResponse(BaseModel):
    action: str
    current_instances: int
    recommended_instances: int
    reason: str
    urgency: str
    cost_impact: dict
    confidence: float

class DashboardStats(BaseModel):
    current_cpu: float
    current_memory: float
    current_network: float
    predicted_cpu: float
    predicted_memory: float
    recommended_action: str
    current_cost_per_hour: float
    monthly_cost: float
    potential_savings: float
    savings_percentage: float


