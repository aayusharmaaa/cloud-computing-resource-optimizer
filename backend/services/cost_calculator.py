from config import settings
from typing import Dict

class CostCalculator:
    def __init__(self):
        self.instance_cost_per_hour = settings.instance_cost_per_hour
        self.cost_per_cpu_percent = settings.cost_per_cpu_percent
    
    def calculate_current_cost(self, cpu_utilization: float, memory_utilization: float, instance_count: int = 1) -> float:
        """Calculate current hourly cost"""
        base_cost = self.instance_cost_per_hour * instance_count
        utilization_cost = (cpu_utilization / 100) * self.cost_per_cpu_percent * instance_count
        return base_cost + utilization_cost
    
    def calculate_predicted_cost(self, predicted_cpu: float, predicted_memory: float, instance_count: int = 1) -> float:
        """Calculate predicted hourly cost"""
        return self.calculate_current_cost(predicted_cpu, predicted_memory, instance_count)
    
    def calculate_scaling_cost_impact(self, current_instances: int, new_instances: int, avg_utilization: float) -> Dict:
        """Calculate cost impact of scaling"""
        current_cost = self.calculate_current_cost(avg_utilization, avg_utilization, current_instances)
        new_cost = self.calculate_current_cost(avg_utilization, avg_utilization, new_instances)
        cost_difference = new_cost - current_cost
        
        # Calculate potential savings from right-sizing
        optimal_instances = max(1, int(current_instances * (avg_utilization / 70)))
        optimal_cost = self.calculate_current_cost(avg_utilization, avg_utilization, optimal_instances)
        potential_savings = current_cost - optimal_cost
        
        return {
            "current_cost": round(current_cost, 4),
            "new_cost": round(new_cost, 4),
            "cost_difference": round(cost_difference, 4),
            "optimal_instances": optimal_instances,
            "optimal_cost": round(optimal_cost, 4),
            "potential_savings": round(potential_savings, 4),
            "savings_percentage": round((potential_savings / current_cost * 100) if current_cost > 0 else 0, 2)
        }
    
    def calculate_monthly_cost(self, hourly_cost: float) -> float:
        """Calculate monthly cost from hourly"""
        return hourly_cost * 24 * 30
    
    def calculate_annual_cost(self, hourly_cost: float) -> float:
        """Calculate annual cost from hourly"""
        return hourly_cost * 24 * 365


