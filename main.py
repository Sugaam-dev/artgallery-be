# # main.py
# from fastapi import FastAPI, Depends, HTTPException, Query # Added Query
# from sqlalchemy.orm import Session
# from sqlalchemy import select, desc
# from typing import List, Optional #
# from database import get_db, engine
# from models import Base, Product, ProductSchema
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr


# app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
#     "*", # Wildcard allows access from any domain (Use only for development/testing)
#     # Add your specific frontend URL here, e.g., "https://your-frontend-domain.com"
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,          # List of allowed origins
#     allow_credentials=True,         # Allow cookies/authorization headers
#     allow_methods=["*"],            # Allow all methods (GET, POST, PUT, DELETE, etc.)
#     allow_headers=["*"],            # Allow all headers
# )

# # Optional: Function to create tables if they don't exist (useful for testing)
# # You don't need this if your table is already created manually.
# # Base.metadata.create_all(bind=engine) 

# # --- GET API to fetch all products ---

# class LoginSchema(BaseModel):
#     email: EmailStr 

# @app.post("/auth/login-init")
# async def login_init(user_data: LoginSchema):
#     # Logic: Check your database for the email
#     # For now, we'll just return a success message
#     return {"message": "Email received", "email": user_data.email} 



# @app.get("/products/", response_model=List[ProductSchema])
# def read_products(
#     category: Optional[str] = Query(None), 
#     limit: Optional[int] = Query(None),  # Add this to accept the "number"
#     db: Session = Depends(get_db)
# ):
#     # 1. Start with the base select statement
#     statement = select(Product)
    
#     # 2. Check for the 'New' category condition
#     if category == 'New':
#         statement = statement.order_by(desc(Product.date))
#         # If the user didn't provide a specific limit, default to 30 for 'New'
#         limit = limit or 30
    
#     # 3. Handle specific category filters
#     elif category:
#         statement = statement.where(Product.category == category)

#     # 4. Apply the limit if provided (e.g., first 10 or 15)
#     if limit:
#         statement = statement.limit(limit)

#     # 5. Execute the statement
#     results = db.execute(statement).scalars().all()
    
#     return results

# # --- GET API to fetch a single product by ID (Unchanged) ---
# @app.get("/products/{product_id}", response_model=ProductSchema)
# def read_product_by_id(product_id: int, db: Session = Depends(get_db)):
#     product = db.get(Product, product_id)
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import your local files
from database import get_db, engine
from models import Base, Product, ProductSchema, User  # Ensure User is in models.py
from schemas import UserCreate, UserOut, Token  # Create these in schemas.py
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# --- SECURITY CONFIGURATION ---
SECRET_KEY = "your_secret_key_here" # Keep this very safe!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI()

# --- CORS ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH UTILS ---
def hash_password(password: str):
    # Simply returns the plain string now
    return password

def verify_password(plain_password, stored_password):
    # Direct string comparison
    return plain_password == stored_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to protect routes
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ENDPOINTS ---

@app.post("/auth/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash password and save
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password), 
        full_name=user_data.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Direct comparison check
    if not user or not (form_data.password == user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # access_token = create_access_token(data={"sub": user.email})
    # return {"access_token": access_token, "token_type": "bearer"}
    return {"message": "Login successful"}

# --- PRODUCT ENDPOINTS (Your Existing Logic) ---

@app.get("/products/", response_model=List[ProductSchema])
def read_products(
    category: Optional[str] = Query(None), 
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    statement = select(Product)
    if category == 'New':
        statement = statement.order_by(desc(Product.date))
        limit = limit or 30
    elif category:
        statement = statement.where(Product.category == category)

    if limit:
        statement = statement.limit(limit)

    results = db.execute(statement).scalars().all()
    return results

@app.get("/products/{product_id}", response_model=ProductSchema)
def read_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# --- PROTECTED ROUTE EXAMPLE ---
# @app.get("/users/me", response_model=UserOut)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user

# --- PROTECTED ROUTE (Get Current User) ---
@app.get("/users/me", response_model=UserOut)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user