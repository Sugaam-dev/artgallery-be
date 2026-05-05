# # models.py

# from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Boolean
# from pydantic import BaseModel
# from sqlalchemy.dialects.postgresql import ARRAY  # Use this for the DB column
# from typing import List
# from database import Base
# import datetime

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     is_admin = Column(Boolean, default=False) # Roles: False = User, True = Admin
#     full_name = Column(String)

# # 1. SQLAlchemy ORM Model (Maps to the 'products' table)
# class Product(Base):
#     __tablename__ = "products"
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String)
#     price = Column(Numeric(10, 2))
#     image = Column(String)
#     description = Column(Text)
#     slug = Column(String, unique=True)
#     category = Column(Text)
#     date = Column(DateTime, default=datetime.datetime.utcnow)
#     sizes = Column(ARRAY(String), default=[])      # Stores ['XS', 'S', 'M']
#     materials = Column(ARRAY(String), default=[])  # Stores ['CANVAS', 'WOOD']
#     frames = Column(ARRAY(String), default=[])     # Stores ['BLACK FRAME', 'GOLD']
#     images = Column(ARRAY(String), default=[])     # Stores ['img1', 'img2', ...]

# # 2. Pydantic Schema (Defines the structure of the JSON response)
# class ProductSchema(BaseModel):
#     # Note: price is float in Python, even though it's Numeric in SQL
#     id: int
#     title: str
#     price: float
#     image: str | None # | None means it can be a string or null
#     description: str | None
#     slug: str
#     category: str | None  # Added category field for filtering
#     date: datetime.datetime | None
#     # Lists match the PSQL Array structure
#     sizes: List[str] = []
#     materials: List[str] = []
#     frames: List[str] = []
#     images: List[str] = []

#     class Config:
#         # This tells Pydantic to convert the ORM object to a Python dict
#         # It handles the conversion of SQLAlchemy objects for you.
#         from_attributes = True # for FastAPI v0.104.0+
#         # orm_mode = True # for older FastAPI versions

# # Note: Ensure that your database supports the ARRAY type (e.g., PostgreSQL).

from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Boolean
from pydantic import BaseModel, EmailStr
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List, Optional
from database import Base
from datetime import datetime, timedelta, timezone

# --- 1. DATABASE MODELS (SQLAlchemy) ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Numeric(10, 2))
    image = Column(String)
    description = Column(Text)
    slug = Column(String, unique=True)
    category = Column(Text)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sizes = Column(ARRAY(String), default=[])
    materials = Column(ARRAY(String), default=[])
    frames = Column(ARRAY(String), default=[])
    images = Column(ARRAY(String), default=[])

# --- 2. SCHEMAS (Pydantic / JSON Validation) ---

# For Product Responses
class ProductSchema(BaseModel):
    id: int
    title: str
    price: float
    image: Optional[str] = None
    description: Optional[str] = None
    slug: str
    category: Optional[str] = None
    date: Optional[datetime] = None
    sizes: List[str] = []
    materials: List[str] = []
    frames: List[str] = []
    images: List[str] = []

    class Config:
        from_attributes = True

# For Creating a User (Incoming data from React)
""""
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

# For Sending User data back (Outgoing data to React - NO PASSWORD)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_admin: bool

    class Config:
        from_attributes = True
        """

# For JWT Tokens
class Token(BaseModel):
    access_token: str
    token_type: str



