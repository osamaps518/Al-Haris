from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import requests, os, random, string

from app.database import get_db
from app.auth import verify_password, create_access_token, decode_access_token, hash_password
from app.queries import (
    get_parent_by_email,
    email_exists,
    create_parent,
    create_verification_code,
    get_verification_code,
    mark_code_used
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

#          DTOs

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @field_validator('password')
    @classmethod  
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class LoginRequest(BaseModel):
    email: str
    password: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

#          Helpers

def generate_code(length=6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email: str, code: str) -> None:
    url = os.getenv("RESEND_API_URL")
    payload = {
        "from": os.getenv("FROM_EMAIL"),
        "to": email,
        "subject": "Your Verification Code",
        "html": f"<strong>Your verification code is: {code}</strong><br>Valid for 10 minutes."
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Email error: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to send email")

def get_current_parent(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    parent_id = payload.get("parent_id")
    result = db.execute(text("SELECT id, email, name FROM parent WHERE id = :id"), {"id": parent_id}).fetchone()
    if not result:
        raise HTTPException(status_code=401, detail="Parent not found")
    
    return {"id": result[0], "email": result[1], "name": result[2]}

#          Endpoints

@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    if email_exists(db, request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(request.password)
    parent_id = create_parent(db, request.email, hashed, request.name)
    
    # Send verification code
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    create_verification_code(db, parent_id, code, expires_at)
    send_verification_email(request.email, code)
    
    return {"message": "Account created. Verification code sent."}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    parent = get_parent_by_email(db, request.email)
    if not parent or not verify_password(request.password, parent[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    parent_id = parent[0]
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    create_verification_code(db, parent_id, code, expires_at)
    send_verification_email(request.email, code)
    
    return {"message": "Verification code sent"}

@router.post("/verify")
def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    parent = get_parent_by_email(db, request.email)
    if not parent:
        raise HTTPException(status_code=401, detail="Invalid email")
    
    parent_id = parent[0]
    result = get_verification_code(db, parent_id, request.code)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired code")
    
    code_id, expires_at = result
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=401, detail="Code expired")
    
    mark_code_used(db, code_id)
    
    access_token = create_access_token({"parent_id": parent_id, "email": request.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_current_parent_details(parent: dict = Depends(get_current_parent)):
    return {"name": parent["name"]}