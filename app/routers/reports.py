from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.screenshots import capture_screenshot
from app.database import get_db
from app.routers.auth import get_current_parent
from app.queries import (
    get_child_with_parent,
    create_report,
    get_parent_blocked_urls,
    get_parent_enabled_categories,
    get_reports_by_parent
)

router = APIRouter(tags=["reports"])

# ========================================
#          DTOs
# ========================================

class SubmitReportRequest(BaseModel):
    child_id: int
    website_url: str

# ========================================
#          Endpoints
# ========================================

@router.get("/parent/reports")
def get_reports(parent: dict = Depends(get_current_parent), db: Session = Depends(get_db)):
    reports = get_reports_by_parent(db, parent["id"])
    return {"reports": [
        {
            "id": r[0],
            "website_url": r[1],
            "screenshot_url": r[2],
            "timestamp": r[3].isoformat(),
            "child_name": r[4]
        }
        for r in reports
    ]}

@router.post("/child/report")
def submit_report(request: SubmitReportRequest, db: Session = Depends(get_db)):
    child = get_child_with_parent(db, request.child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    # Normalize domain
    domain = request.website_url.strip().lower()
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    domain = domain.rstrip('/').split('/')[0]
    
    from app.blocklists import _blocklists, OPTIONAL_CATEGORIES
    
    # Find which category blocked it (priority order)
    blocking_reason = None
    
    # Check gambling first (before adult, since adult list contains some gambling sites)
    if domain in _blocklists.get("gambling", set()):
        blocking_reason = "gambling"
    elif domain in _blocklists.get("violence", set()):
        blocking_reason = "violence"
    elif domain in _blocklists.get("games", set()):
        blocking_reason = "games"
    elif domain in _blocklists.get("chat", set()):
        blocking_reason = "chat"
    elif domain in _blocklists.get("adult", set()):
        blocking_reason = "adult"
    
    print(f"DEBUG: {domain} -> blocking_reason: {blocking_reason}")
    
    # Only skip screenshot for truly adult content
    screenshot_url = None
    if blocking_reason != "adult":
        screenshot_url = capture_screenshot(request.website_url)
    
    report_id = create_report(db, request.child_id, request.website_url, screenshot_url)
    return {
        "message": "Report submitted", 
        "report_id": report_id, 
        "screenshot_captured": blocking_reason != "adult",
        "blocked_reason": blocking_reason
    }