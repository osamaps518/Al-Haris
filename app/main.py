from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.auth import verify_password, create_access_token, decode_access_token
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Dict

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


@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    parent = get_parent_by_email(db, request.email)
    
    if not parent or not verify_password(request.password, parent[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    parent_id = parent[0]
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    
    create_verification_code(db, parent_id, code, expires_at)
    
    # TODO: Send email
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
    if datetime.now() > expires_at:
        raise HTTPException(status_code=401, detail="Code expired")
    
    mark_code_used(db, code_id)
    
    access_token = create_access_token({"parent_id": parent_id, "email": request.email})
    return {"access_token": access_token, "token_type": "bearer"}