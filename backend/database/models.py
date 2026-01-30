"""
Database models for school bus routing system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime

class Bus(Base):
    __tablename__ = 'buses'
    
    id = Column(Integer, primary_key=True)
    bus_number = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    fuel_efficiency = Column(Float)  # km per liter
    status = Column(String(20), default='active')  # active, maintenance, retired
    current_location = Column(JSON)  # {lat: float, lng: float}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    routes = relationship('Route', back_populates='bus')
    tracking_data = relationship('TrackingData', back_populates='bus')

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    grade = Column(String(10))
    home_address = Column(String(255))
    home_location = Column(JSON)  # {lat: float, lng: float}
    parent_contact = Column(String(20))
    parent_email = Column(String(100))
    assigned_stop_id = Column(Integer, ForeignKey('stops.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assigned_stop = relationship('Stop', back_populates='students')

class Stop(Base):
    __tablename__ = 'stops'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(JSON, nullable=False)  # {lat: float, lng: float}
    address = Column(String(255))
    pickup_time = Column(DateTime)
    dropoff_time = Column(DateTime)
    student_count = Column(Integer, default=0)
    geofence_radius = Column(Float, default=100)  # meters
    
    students = relationship('Student', back_populates='assigned_stop')
    route_stops = relationship('RouteStop', back_populates='stop')

class Route(Base):
    __tablename__ = 'routes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    bus_id = Column(Integer, ForeignKey('buses.id'))
    route_type = Column(String(20))  # pickup, dropoff
    total_distance = Column(Float)  # kilometers
    estimated_duration = Column(Integer)  # minutes
    optimization_score = Column(Float)  # AI optimization score
    ai_metadata = Column(JSON)  # Store AI decisions and metrics
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bus = relationship('Bus', back_populates='routes')
    route_stops = relationship('RouteStop', back_populates='route', order_by='RouteStop.sequence')

class RouteStop(Base):
    __tablename__ = 'route_stops'
    
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    stop_id = Column(Integer, ForeignKey('stops.id'))
    sequence = Column(Integer, nullable=False)  # Order in route
    arrival_time = Column(DateTime)
    departure_time = Column(DateTime)
    distance_from_previous = Column(Float)  # kilometers
    
    route = relationship('Route', back_populates='route_stops')
    stop = relationship('Stop', back_populates='route_stops')

class TrackingData(Base):
    __tablename__ = 'tracking_data'
    
    id = Column(Integer, primary_key=True)
    bus_id = Column(Integer, ForeignKey('buses.id'))
    location = Column(JSON, nullable=False)  # {lat: float, lng: float}
    speed = Column(Float)  # km/h
    heading = Column(Float)  # degrees
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    accuracy = Column(Float)  # meters
    
    bus = relationship('Bus', back_populates='tracking_data')

class DemandForecast(Base):
    __tablename__ = 'demand_forecasts'
    
    id = Column(Integer, primary_key=True)
    stop_id = Column(Integer, ForeignKey('stops.id'))
    forecast_date = Column(DateTime, nullable=False)
    predicted_count = Column(Integer)
    confidence = Column(Float)  # 0-1
    model_version = Column(String(20))
    features = Column(JSON)  # Store feature values used
    created_at = Column(DateTime, default=datetime.utcnow)

class OptimizationHistory(Base):
    __tablename__ = 'optimization_history'
    
    id = Column(Integer, primary_key=True)
    algorithm = Column(String(50))  # genetic, rl, hybrid
    input_params = Column(JSON)
    output_routes = Column(JSON)
    metrics = Column(JSON)  # distance, time, fuel, efficiency
    execution_time = Column(Float)  # seconds
    xai_explanation = Column(JSON)  # SHAP/LIME values
    created_at = Column(DateTime, default=datetime.utcnow)
