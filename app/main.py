from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.auth import verify_password, create_access_token, decode_access_token, hash_password
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

import requests, os, random, string

# TODO: Adjust Ordering of functions so they read smoothly
from app.database import (
    get_db, 
    get_parent_by_email, 
    get_parent_by_id,
    create_verification_code,
    get_verification_code,
    mark_code_used
)


app = FastAPI(title="Al-Haris API", version="0.1.0")
security = HTTPBearer()

# Request models(DTOs)
class LoginRequest(BaseModel):
    email: str
    password: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

@app.get("/")
def root():
    return {"message": "Hello Veil Citizens!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
    

@app.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Simple query to test connection
        result = db.execute(text("SELECT COUNT(*) FROM parent")).fetchone()
        return {"status": "connected", "parent_count": result[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT r.id, r.website_url, r.screenshot_url, r.timestamp, c.name as child_name
        FROM report r
        JOIN child c ON r.child_id = c.id
        ORDER BY r.timestamp DESC
    """)).fetchall()
    
    return {"reports": [
        {
            "id": row[0],
            "website_url": row[1],
            "screenshot_url": row[2],
            "timestamp": row[3].isoformat(),
            "child_name": row[4]
        }
        for row in result
    ]}

# TODO: Add Left Endpoints: 1) Bring blocklist, 2)send blocklist to client device
#     : 3) Receive new blocks from Parent and update database 
#     : 4) Deactivate Parent account 
#     : 5) Reset Password
#     : 6) Make Operations asyn, to not block the main application thread
#     : 7) Write documentation of the Endpoints
#     : 8) Deploy the app, either to docker hub as an image or deploy to railway
#     : 9) Add tests to the main core of the application, CI? What tests do you need? 
#          No need for unit tests 'probably?' as there is no compelx algorithms or logic 
#          to be tested
#     : 10) VERY IMPORTANT: MAKE THE SERVER TAKE THE WEBSITE URL, AND EXTRACT A SCREENSHOT 
#           OFF OF IT, AND THEN SAVE IT TO DATABASE, AND THEN SEREVR SENDS THAT SCREENSHOT 
#           TO PARENT CLIENT
#     : 11) Write README file
#     : 12) Remove Security Risks, like returning the verification code in the json response

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

# TODO: Add Verification Code to Signup, for now its only for login
@app.post("/auth/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    try:
        # TODO: MOVE QUERY Syntax INTO database.py
        existing = db.execute(text("SELECT id FROM parent WHERE email = :email"), {"email": request.email}).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        

        # TODO: MOVE QUERY Syntax INTO database.py
        # hashed = hash_password(request.password[:72]) 
        hashed = hash_password(request.password)
        db.execute(text("""
            INSERT INTO parent (email, password_hash, name)
            VALUES (:email, :password, :name)
        """), {"email": request.email, "password": hashed, "name": request.name})
        db.commit()
        
        return {"message": "Account created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")  # Check docker logs
        raise HTTPException(status_code=500, detail=str(e))

# TODO: ONLY FOR TESTING PURPOSES, REMOVE AFTERWARDS
@app.get("/debug/parents")
def get_all_parents(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT id, email, name FROM parent")).fetchall()
    return [{"id": r[0], "email": r[1], "name": r[2]} for r in result]

# TODO: ONLY FOR TESTING PURPOSES, REMOVE AFTERWARDS
@app.get("/debug/verification-codes")
def get_all_verification_codes(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT id, parent_id, code, expires_at, is_used, created_at 
        FROM verification_code
        ORDER BY created_at DESC
    """)).fetchall()
    return [{"id": r[0], "parent_id": r[1], "code": r[2], "expires_at": r[3].isoformat() if r[3] else None, "is_used": r[4], "created_at": r[5].isoformat() if r[5] else None} for r in result]

# Auth dependency
# TODO: This function will is subject to be moved to other more fitting file
def get_current_parent(credentials: HTTPAuthorizationCredentials = 
                       Depends(security), db: Session = Depends(get_db)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    parent_id = payload.get("parent_id")
    result = db.execute(text("SELECT id, email, name FROM parent WHERE id = :id"), {"id": parent_id}).fetchone()
    if not result:
        raise HTTPException(status_code=401, detail="Parent not found")
    
    return {"id": result[0], "email": result[1], "name": result[2]}

# Generate verification code
# TODO: This function will is subject to be moved to other more fitting file
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email: str, code: str):
    url = os.getenv("RESEND_API_URL")
        
    payload = {
        "from": os.getenv("FROM_EMAIL"),
        "to": "osamams518@gmail.com",
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


@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    parent = get_parent_by_email(db, request.email)
    print (parent[1])
    
    if not parent or not verify_password(request.password, parent[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    parent_id = parent[0]
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    create_verification_code(db, parent_id, code, expires_at)
    send_verification_email(request.email, code)
    
    return {"message": "Verification code sent", "code": code}

@app.post("/auth/verify")
def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    parent = get_parent_by_email(db, request.email)
    if not parent:
        raise HTTPException(status_code=401, detail="Invalid email")
    
    parent_id = parent[0]
    result = get_verification_code(db, parent_id, request.code)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired code")
    
    code_id, expires_at = result
    # Handle naive datetime from database by adding UTC timezone
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=401, detail="Code expired")
    
    mark_code_used(db, code_id)
    
    access_token = create_access_token({"parent_id": parent_id, "email": request.email})
    return {"access_token": access_token, "token_type": "bearer"}