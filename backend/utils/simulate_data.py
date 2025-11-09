import numpy as np
from datetime import datetime, timedelta
import random

class DataSimulator:
    def __init__(self):
        self.base_cpu = 60.0
        self.base_memory = 55.0
        self.trend = 0.0
        self.time_step = 0
        
    def _generate_realistic_pattern(self, base_value, variance=15.0, trend_factor=0.1):
        """Generate realistic time-series data with trends and patterns"""
        # Add some trend
        trend = np.sin(self.time_step / 20.0) * 10
        seasonal = np.sin(self.time_step / 10.0) * 8
        
        # Add some noise
        noise = np.random.normal(0, variance / 3)
        
        # Add occasional spikes
        spike = 0
        if random.random() < 0.1:  # 10% chance of spike
            spike = random.uniform(20, 40) if random.random() > 0.5 else -random.uniform(10, 20)
        
        value = base_value + trend + seasonal + noise + spike
        self.time_step += 1
        
        # Clamp to realistic range
        return max(10, min(95, value))
    
    def get_mock_cpu_data(self, n=10):
        """Generate realistic CPU utilization data"""
        return [self._generate_realistic_pattern(self.base_cpu, 15.0) for _ in range(n)]
    
    def get_mock_memory_data(self, n=10):
        """Generate realistic memory utilization data"""
        return [self._generate_realistic_pattern(self.base_memory, 12.0) for _ in range(n)]
    
    def get_mock_network_data(self, n=10):
        """Generate realistic network I/O data (in MB/s)"""
        base_network = 45.0
        return [self._generate_realistic_pattern(base_network, 10.0) for _ in range(n)]
    
    def get_current_metrics(self):
        """Get current metric values"""
        return {
            "cpu": self._generate_realistic_pattern(self.base_cpu, 15.0),
            "memory": self._generate_realistic_pattern(self.base_memory, 12.0),
            "network": self._generate_realistic_pattern(45.0, 10.0),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def update_base_values(self, cpu_change=0, memory_change=0):
        """Update base values to simulate scaling"""
        self.base_cpu = max(20, min(90, self.base_cpu + cpu_change))
        self.base_memory = max(20, min(90, self.base_memory + memory_change))

# Global simulator instance
simulator = DataSimulator()

def get_mock_cpu_data():
    return simulator.get_mock_cpu_data()
