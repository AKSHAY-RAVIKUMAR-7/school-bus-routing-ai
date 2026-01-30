"""
Database connection and initialization
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import Config
import redis
import os

# Use SQLite for development if PostgreSQL not available
db_url = Config.DATABASE_URL
if 'postgresql' in db_url and not os.getenv('USE_POSTGRESQL', False):
    db_url = 'sqlite:///school_bus.db'
    print(f"Using SQLite database: {db_url}")

# SQLAlchemy setup
engine = create_engine(db_url, echo=Config.DEBUG)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

# Redis setup (with fallback)
try:
    redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
except:
    print("Redis not available, using in-memory fallback")
    redis_client = None

def init_db():
    """Initialize database tables"""
    import database.models  # Import models to register them
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
