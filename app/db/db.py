import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

# Initialize global Cloud SQL Connector
#connector = Connector()  # will use Application Default Credentials if running on GCP

# Replace getconn() with direct connection when INSTANCE_CONNECTION_NAME == "local"
def getconn():
    
        import pymysql
        return pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,
        )
    


# SQLAlchemy engine using the connector as creator
engine = create_engine(
    "mysql+pymysql://",
    creator=getconn,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_timeout=30,
    pool_recycle=1800,
)

# Use scoped_session for thread-safety in web apps
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
