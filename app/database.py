from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

import os

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
# ========================================
#          Authentication queries
# ========================================
def get_parent_by_email(db: Session, email: str) -> Optional[tuple]:
    return db.execute(
        text("SELECT id, password_hash, name FROM parent WHERE email = :email"),
        {"email": email}
    ).fetchone()

def get_parent_by_id(db: Session, parent_id: int) -> Optional[tuple]:
    return db.execute(
        text("SELECT id, email, name FROM parent WHERE id = :id"),
        {"id": parent_id}
    ).fetchone()

def create_verification_code(db: Session, parent_id: int, code: str, expires_at: datetime) -> None:
    db.execute(text("""
        INSERT INTO verification_code (parent_id, code, expires_at)
        VALUES (:parent_id, :code, :expires_at)
    """), {"parent_id": parent_id, "code": code, "expires_at": expires_at})
    db.commit()

def get_verification_code(db: Session, parent_id: int, code: str) -> Optional[tuple]:
    return db.execute(text("""
        SELECT id, expires_at FROM verification_code 
        WHERE parent_id = :parent_id AND code = :code AND is_used = FALSE
        ORDER BY created_at DESC LIMIT 1
    """), {"parent_id": parent_id, "code": code}).fetchone()

def mark_code_used(db: Session, code_id: int) -> None:
    db.execute(text("UPDATE verification_code SET is_used = TRUE WHERE id = :id"), {"id": code_id})
    db.commit()