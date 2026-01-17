# database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)  # Debugging line to check if the URL is loaded correctly

# 1. Create the SQLAlchemy Engine
# The engine is the source of database connections
engine = create_engine(DATABASE_URL)

# 2. Create a SessionLocal class
# This class will be an actual database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create a Base class for your models
Base = declarative_base()

# 4. Dependency to get a DB session
# This function creates a new session for each request and closes it afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()