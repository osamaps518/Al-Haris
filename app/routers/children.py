from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import get_current_parent
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
    return {
        "enabled_categories": get_parent_enabled_categories(db, parent_id),
        "blocked_urls": get_parent_blocked_urls(db, parent_id)
    }