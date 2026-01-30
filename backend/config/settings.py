"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Frontend URL for CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3001')
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/school_bus')
    # For production on Render, use SQLite if no PostgreSQL
    if 'RENDER' in os.environ and not DATABASE_URL.startswith('postgresql'):
        DATABASE_URL = 'sqlite:///school_bus.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis settings (optional in production)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # MQTT settings
    MQTT_BROKER_URL = os.getenv('MQTT_BROKER', 'localhost')
    MQTT_BROKER_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
    MQTT_KEEPALIVE = 60
    MQTT_TLS_ENABLED = False
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    # AI Model settings
    MODEL_PATH = 'ml_models/'
    GENETIC_ALGORITHM_GENERATIONS = 100
    GENETIC_ALGORITHM_POPULATION = 50
    RL_EPISODES = 1000
    DL_EPOCHS = 50
    
    # Real-time settings
    GPS_UPDATE_INTERVAL = 10  # seconds
    GEOFENCE_RADIUS = 100  # meters
    
    # XAI settings
    SHAP_SAMPLE_SIZE = 100
    LIME_NUM_FEATURES = 10
