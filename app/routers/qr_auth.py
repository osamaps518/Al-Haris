from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets

from app.database import get_db
from app.routers.auth import get_current_parent
from app.auth import create_access_token
from app.queries import (
    get_child_with_parent,
    create_qr_token,
    get_qr_token,
    mark_qr_token_used
)

router = APIRouter(prefix="/auth", tags=["qr-auth"])

#          DTOs

class GenerateQRRequest(BaseModel):
    child_id: int

class QRLoginRequest(BaseModel):
    token: str

#          Endpoints

@router.post("/generate-qr-token")
def generate_qr_token(
    request: GenerateQRRequest,
    parent: dict = Depends(get_current_parent),
    db: Session = Depends(get_db)
):
    """Parent generates a QR token for a specific child"""
    child = get_child_with_parent(db, request.child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    if child[1] != parent["id"]:  # child[1] is parent_id
        raise HTTPException(status_code=403, detail="Child does not belong to you")
    
    # Generate secure random token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=3)
    
    create_qr_token(db, token, parent["id"], request.child_id, expires_at)
    
    return {
        "token": token,
        "child_name": child[2],  # child[2] is name
        "expires_at": expires_at.isoformat()
    }

@router.post("/login-qr")
def login_with_qr(request: QRLoginRequest, db: Session = Depends(get_db)):
    """Child device logs in using scanned QR token"""
    result = get_qr_token(db, request.token)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired QR token")
    
    token_id, parent_id, child_id, expires_at, is_used = result
    
    if is_used:
        raise HTTPException(status_code=401, detail="QR token already used")
    
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=401, detail="QR token expired")
    
    mark_qr_token_used(db, token_id)
    
    # Generate JWT for the child
    access_token = create_access_token({
        "child_id": child_id,
        "parent_id": parent_id
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "child_id": child_id
    }