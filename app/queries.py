from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Optional

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

def create_parent(db: Session, email: str, password_hash: str, name: str) -> int:
    result = db.execute(text("""
        INSERT INTO parent (email, password_hash, name)
        VALUES (:email, :password_hash, :name)
        RETURNING id
    """), {"email": email, "password_hash": password_hash, "name": name})
    db.commit()
    return result.fetchone()[0]

def email_exists(db: Session, email: str) -> bool:
    result = db.execute(
        text("SELECT id FROM parent WHERE email = :email"), 
        {"email": email}
    ).fetchone()
    return result is not None

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
#          Child queries
# ========================================

def get_children_by_parent(db: Session, parent_id: int) -> list[tuple]:
    return db.execute(text("""
        SELECT id, name, device_name, created_at FROM child 
        WHERE parent_id = :parent_id
    """), {"parent_id": parent_id}).fetchall()

def create_child(db: Session, parent_id: int, name: str, device_name: str | None) -> int:
    result = db.execute(text("""
        INSERT INTO child (parent_id, name, device_name)
        VALUES (:parent_id, :name, :device_name)
        RETURNING id
    """), {"parent_id": parent_id, "name": name, "device_name": device_name})
    db.commit()
    return result.fetchone()[0]

def get_child_with_parent(db: Session, child_id: int) -> tuple | None:
    return db.execute(text("""
        SELECT id, parent_id, name, device_name FROM child WHERE id = :child_id
    """), {"child_id": child_id}).fetchone()

def delete_child_by_id(db: Session, child_id: int) -> None:
    db.execute(text("DELETE FROM child WHERE id = :id"), {"id": child_id})
    db.commit()


# ========================================
#          Blocklist queries
# ========================================

def get_parent_enabled_categories(db: Session, parent_id: int) -> list[str]:
    result = db.execute(text("""
        SELECT category FROM blocked_category 
        WHERE parent_id = :parent_id
    """), {"parent_id": parent_id}).fetchall()
    return [row[0] for row in result]

def set_parent_category(db: Session, parent_id: int, category: str, enabled: bool) -> None:
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
    result = db.execute(text("""
        SELECT url FROM blocked_url WHERE parent_id = :parent_id
    """), {"parent_id": parent_id}).fetchall()
    return [row[0] for row in result]

def add_blocked_url(db: Session, parent_id: int, url: str) -> None:
    db.execute(text("""
        INSERT INTO blocked_url (parent_id, url)
        VALUES (:parent_id, :url)
        ON CONFLICT (parent_id, url) DO NOTHING
    """), {"parent_id": parent_id, "url": url})
    db.commit()

def remove_blocked_url(db: Session, parent_id: int, url: str) -> bool:
    result = db.execute(text("""
        DELETE FROM blocked_url 
        WHERE parent_id = :parent_id AND url = :url
        RETURNING id
    """), {"parent_id": parent_id, "url": url})
    db.commit()
    return result.fetchone() is not None

# ========================================
#          Report queries
# ========================================

def create_report(db: Session, child_id: int, website_url: str, screenshot_url: str | None) -> int:
    result = db.execute(text("""
        INSERT INTO report (child_id, website_url, screenshot_url)
        VALUES (:child_id, :website_url, :screenshot_url)
        RETURNING id
    """), {"child_id": child_id, "website_url": website_url, "screenshot_url": screenshot_url})
    db.commit()
    return result.fetchone()[0]

def get_reports_by_parent(db: Session, parent_id: int) -> list[tuple]:
    return db.execute(text("""
        SELECT r.id, r.website_url, r.screenshot_url, r.timestamp, c.name as child_name
        FROM report r
        JOIN child c ON r.child_id = c.id
        WHERE c.parent_id = :parent_id
        ORDER BY r.timestamp DESC
    """), {"parent_id": parent_id}).fetchall()

# ========================================
#          App Status queries
# ========================================

def get_parent_app_status(db: Session, parent_id: int) -> bool:
    result = db.execute(
        text("SELECT filtering_enabled FROM parent WHERE id = :id"),
        {"id": parent_id}
    ).fetchone()
    return result[0] if result else True

def set_parent_app_status(db: Session, parent_id: int, enabled: bool) -> None:
    db.execute(
        text("UPDATE parent SET filtering_enabled = :enabled WHERE id = :id"),
        {"enabled": enabled, "id": parent_id}
    )
    db.commit()


