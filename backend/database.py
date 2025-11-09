from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()

class MetricRecord(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_utilization = Column(Float)
    memory_utilization = Column(Float)
    network_io = Column(Float)
    cost = Column(Float)
    instance_count = Column(Integer, default=1)
    
class PredictionRecord(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    predicted_cpu = Column(Float)
    predicted_memory = Column(Float)
    recommended_action = Column(String)
    confidence = Column(Float)
    cost_savings = Column(Float)

class ActionHistory(Base):
    __tablename__ = "action_history"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    action = Column(String)
    previous_instance_count = Column(Integer)
    new_instance_count = Column(Integer)
    reason = Column(String)
    cost_impact = Column(Float)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


