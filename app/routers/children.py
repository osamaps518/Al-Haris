from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import get_current_parent
from app.blocklists import is_domain_blocked
from app.queries import (
    get_children_by_parent,
    create_child,
    get_child_with_parent,
    get_parent_enabled_categories,
    get_parent_blocked_urls
)

router = APIRouter(tags=["children"])

# ========================================
#          DTOs
# ========================================

class CreateChildRequest(BaseModel):
    name: str
    device_name: str | None = None
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

# ========================================
#          Parent Endpoints
# ========================================

@router.get("/parent/children")
def list_children(parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    children = get_children_by_parent(db, parent["id"])
    return {"children": [
        {"id": c[0], "name": c[1], "device_name": c[2], "created_at": c[3].isoformat()}
        for c in children
    ]}

@router.post("/parent/child")
def add_child(request: CreateChildRequest, parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    child_id = create_child(db, parent["id"], request.name, request.device_name)
    return {"message": "Child added", "child_id": child_id}

# ========================================
#          Child Device Endpoints
# ========================================

@router.get("/child/{child_id}/blocklist")
def get_child_blocklist(child_id: int, db: Session = Depends(get_db)):
    child = get_child_with_parent(db, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    parent_id = child[1]
    
    from app.queries import get_parent_app_status
    if not get_parent_app_status(db, parent_id):
        return {"enabled_categories": [], "blocked_urls": [], "filtering_enabled": False}
    
    return {
        "enabled_categories": get_parent_enabled_categories(db, parent_id),
        "blocked_urls": get_parent_blocked_urls(db, parent_id),
        "filtering_enabled": True
    }

@router.get("/child/{child_id}/check")
def check_domain(child_id: int, domain: str, db: Session = Depends(get_db)):
    # Normalize domain
    domain = domain.strip().lower()
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    domain = domain.rstrip('/').split('/')[0]  # Remove path
    
    if not domain:
        raise HTTPException(status_code=400, detail="Domain cannot be empty")
    
    child = get_child_with_parent(db, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    parent_id = child[1]
    enabled_categories = get_parent_enabled_categories(db, parent_id)
    blocked_urls = get_parent_blocked_urls(db, parent_id)
    
    from app.blocklists import MANDATORY_CATEGORIES, _blocklists
    
    # Check mandatory first
    for category in MANDATORY_CATEGORIES.keys():
        if domain in _blocklists.get(category, set()):
            return {"blocked": True, "reason": category}
    
    # Check enabled categories
    for category in enabled_categories:
        if domain in _blocklists.get(category, set()):
            return {"blocked": True, "reason": category}
    
    # Check specific URLs
    if domain in blocked_urls:
        return {"blocked": True, "reason": "blocked_url"}
    
    return {"blocked": False, "reason": None}


@router.delete("/parent/child/{child_id}")
def delete_child(child_id: int, parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = get_child_with_parent(db, child_id)
    if not child or child[1] != parent["id"]:
        raise HTTPException(status_code=404, detail="Child not found")
    
    from app.queries import delete_child_by_id
    delete_child_by_id(db, child_id)
    return {"message": "Child deleted"}