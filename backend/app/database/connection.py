import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
import urllib.parse
DB_PASSWORD = os.getenv("DB_PASSWORD", "yourpassword")
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "insurance_rag")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
