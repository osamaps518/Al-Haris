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

# ========================================
#          Blocklist queries
# ========================================

def get_child_enabled_categories(db: Session, child_id: int) -> list[str]:
    """Get list of enabled category names for a child"""
    result = db.execute(text("""
        SELECT category FROM blocked_content 
        WHERE child_id = :child_id AND category IS NOT NULL
    """), {"child_id": child_id}).fetchall()
    return [row[0] for row in result]

def set_child_category(db: Session, child_id: int, category: str, enabled: bool) -> None:
    """Enable or disable a category for a child"""
    if enabled:
        db.execute(text("""
            INSERT INTO blocked_content (child_id, category)
            VALUES (:child_id, :category)
            ON CONFLICT (child_id, category) WHERE category IS NOT NULL DO NOTHING
        """), {"child_id": child_id, "category": category})
    else:
        db.execute(text("""
            DELETE FROM blocked_content 
            WHERE child_id = :child_id AND category = :category
        """), {"child_id": child_id, "category": category})
    db.commit()

def add_specific_blocked_domain(db: Session, child_id: int, domain: str) -> None:
    """Add a specific domain to blocklist for a child"""
    db.execute(text("""
        INSERT INTO blocked_content (child_id, blocked_item)
        VALUES (:child_id, :domain)
    """), {"child_id": child_id, "domain": domain})
    db.commit()