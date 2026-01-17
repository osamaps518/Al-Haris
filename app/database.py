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

def get_parent_enabled_categories(db: Session, parent_id: int) -> list[str]:
    """Get list of enabled category names for a parent"""
    result = db.execute(text("""
        SELECT category FROM blocked_category 
        WHERE parent_id = :parent_id
    """), {"parent_id": parent_id}).fetchall()
    return [row[0] for row in result]

def set_parent_category(db: Session, parent_id: int, category: str, enabled: bool) -> None:
    """Enable or disable a category for a parent"""
    if enabled:
        db.execute(text("""
            INSERT INTO blocked_category (parent_id, category)
            VALUES (:parent_id, :category)
            ON CONFLICT (parent_id, category) DO NOTHING
        """), {"parent_id": parent_id, "category": category})
    else:
        db.execute(text("""
            DELETE FROM blocked_category 
            WHERE parent_id = :parent_id AND category = :category
        """), {"parent_id": parent_id, "category": category})
    db.commit()

def get_parent_blocked_urls(db: Session, parent_id: int) -> list[str]:
    """Get list of specifically blocked URLs for a parent"""
    result = db.execute(text("""
        SELECT url FROM blocked_url WHERE parent_id = :parent_id
    """), {"parent_id": parent_id}).fetchall()
    return [row[0] for row in result]

def add_blocked_url(db: Session, parent_id: int, url: str) -> None:
    """Add a specific URL to blocklist for a parent"""
    db.execute(text("""
        INSERT INTO blocked_url (parent_id, url)
        VALUES (:parent_id, :url)
        ON CONFLICT (parent_id, url) DO NOTHING
    """), {"parent_id": parent_id, "url": url})
    db.commit()

# ========================================
#          Child queries
# ========================================

def get_children_by_parent(db: Session, parent_id: int) -> list[tuple]:
    """Get all children for a parent"""
    return db.execute(text("""
        SELECT id, name, device_name, created_at FROM child 
        WHERE parent_id = :parent_id
    """), {"parent_id": parent_id}).fetchall()

def create_child(db: Session, parent_id: int, name: str, device_name: str | None) -> int:
    """Create a child and return its ID"""
    result = db.execute(text("""
        INSERT INTO child (parent_id, name, device_name)
        VALUES (:parent_id, :name, :device_name)
        RETURNING id
    """), {"parent_id": parent_id, "name": name, "device_name": device_name})
    db.commit()
    return result.fetchone()[0]

def get_child_with_parent(db: Session, child_id: int) -> tuple | None:
    """Get child with parent_id for authorization checks"""
    return db.execute(text("""
        SELECT id, parent_id, name, device_name FROM child WHERE id = :child_id
    """), {"child_id": child_id}).fetchone()

# ========================================
#          Report queries
# ========================================

def create_report(db: Session, child_id: int, website_url: str, screenshot_url: str | None) -> int:
    """Create a report and return its ID"""
    result = db.execute(text("""
        INSERT INTO report (child_id, website_url, screenshot_url)
        VALUES (:child_id, :website_url, :screenshot_url)
        RETURNING id
    """), {"child_id": child_id, "website_url": website_url, "screenshot_url": screenshot_url})
    db.commit()
    return result.fetchone()[0]