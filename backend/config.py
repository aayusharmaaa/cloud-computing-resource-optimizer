import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    api_title: str = "Cloud Resource Optimizer API"
    api_version: str = "1.0.0"
    api_description: str = "AI-Driven Cloud Computing Resource Optimization API"
    
    # CORS Settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database Settings
    database_url: str = "sqlite:///./cloud_optimizer.db"
    
    # Model Settings
    model_dir: str = "./models"
    sequence_length: int = 10
    prediction_horizon: int = 5  # Predict next 5 time steps
    
    # Cost Settings (per hour in USD)
    instance_cost_per_hour: float = 0.10
    cost_per_cpu_percent: float = 0.001
    
    # Scaling Thresholds
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 50.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()


