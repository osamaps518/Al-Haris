from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine
from sqlalchemy import text

app = FastAPI(title="Al-Haris API", version="0.1.0")


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