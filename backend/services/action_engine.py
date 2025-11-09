from config import settings
from services.cost_calculator import CostCalculator
from typing import Dict, Tuple

class ActionEngine:
    def __init__(self):
        self.cost_calculator = CostCalculator()
        self.scale_up_threshold = settings.scale_up_threshold
        self.scale_down_threshold = settings.scale_down_threshold
    
    def get_action(self, predicted_cpu: float, predicted_memory: float, 
                   current_instances: int = 1, confidence: float = 0.7) -> Dict:
        """Determine recommended scaling action"""
        # Adjust thresholds based on confidence
        effective_up_threshold = self.scale_up_threshold + (1 - confidence) * 10
        effective_down_threshold = self.scale_down_threshold - (1 - confidence) * 10
        
        # Use average of CPU and memory for decision
        avg_utilization = (predicted_cpu + predicted_memory) / 2
        
        if avg_utilization > effective_up_threshold:
            new_instances = min(current_instances + 1, 10)  # Cap at 10 instances
            action = "Scale Up"
            reason = f"High utilization predicted ({avg_utilization:.1f}%). Scaling up to handle increased load."
        elif avg_utilization < effective_down_threshold and current_instances > 1:
            new_instances = max(1, current_instances - 1)
            action = "Scale Down"
            reason = f"Low utilization predicted ({avg_utilization:.1f}%). Scaling down to reduce costs."
        else:
            new_instances = current_instances
            action = "Maintain"
            reason = f"Utilization within optimal range ({avg_utilization:.1f}%). Current configuration is appropriate."
        
        cost_impact = self.cost_calculator.calculate_scaling_cost_impact(
            current_instances, new_instances, avg_utilization
        )
        
        return {
            "action": action,
            "current_instances": current_instances,
            "recommended_instances": new_instances,
            "reason": reason,
            "predicted_utilization": round(avg_utilization, 2),
            "confidence": round(confidence, 2),
            "cost_impact": cost_impact,
            "urgency": "high" if abs(avg_utilization - 65) > 20 else "medium" if abs(avg_utilization - 65) > 10 else "low"
        }


