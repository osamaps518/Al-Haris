from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import get_current_parent
from app.blocklists import OPTIONAL_CATEGORIES
from app.queries import (
    get_parent_enabled_categories,
    set_parent_category,
    get_parent_blocked_urls,
    add_blocked_url
)

router = APIRouter(prefix="/parent", tags=["blocking"])

# ========================================
#          DTOs
# ========================================

class UpdateCategoriesRequest(BaseModel):
    categories: list[str]
    
    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        valid = set(OPTIONAL_CATEGORIES.keys())
        invalid = set(v) - valid
        if invalid:
            raise ValueError(f"Invalid categories: {invalid}")
        return v

class BlockUrlRequest(BaseModel):
    url: str
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        v = v.strip().lower()
        if not v:
            raise ValueError('URL cannot be empty')
        # Remove protocol if present
        if v.startswith(('http://', 'https://')):
            v = v.split('://', 1)[1]
        # Remove trailing slash
        return v.rstrip('/')

class UnblockUrlRequest(BaseModel):
    url: str
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        v = v.strip().lower()
        if not v:
            raise ValueError('URL cannot be empty')
        if v.startswith(('http://', 'https://')):
            v = v.split('://', 1)[1]
        return v.rstrip('/')

class AppStatusRequest(BaseModel):
    enabled: bool


# ========================================
#          Endpoints
# ========================================

@router.get("/settings")
def get_blocking_settings(parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    return {
        "enabled_categories": get_parent_enabled_categories(db, parent["id"]),
        "blocked_urls": get_parent_blocked_urls(db, parent["id"]),
        "available_categories": list(OPTIONAL_CATEGORIES.keys())
    }

@router.put("/categories")
def update_categories(request: UpdateCategoriesRequest, parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    current = set(get_parent_enabled_categories(db, parent["id"]))
    desired = set(request.categories)
    
    for cat in current - desired:
        set_parent_category(db, parent["id"], cat, enabled=False)
    
    for cat in desired - current:
        set_parent_category(db, parent["id"], cat, enabled=True)
    
    return {"message": "Categories updated", "enabled_categories": request.categories}

@router.post("/block-url")
def block_url(request: BlockUrlRequest, parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    add_blocked_url(db, parent["id"], request.url)
    return {"message": "URL blocked"}


@router.delete("/unblock-url")
def unblock_url(request: UnblockUrlRequest, parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    from app.queries import remove_blocked_url
    removed = remove_blocked_url(db, parent["id"], request.url)
    if not removed:
        raise HTTPException(status_code=404, detail="URL not found in blocklist")
    return {"message": "URL unblocked"}

@router.put("/app-status")
def set_app_status(request: AppStatusRequest, parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    from app.queries import set_parent_app_status
    set_parent_app_status(db, parent["id"], request.enabled)
    return {"message": "App status updated", "filtering_enabled": request.enabled}

@router.get("/app-status")
def get_app_status(parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    from app.queries import get_parent_app_status
    return {"filtering_enabled": get_parent_app_status(db, parent["id"])}