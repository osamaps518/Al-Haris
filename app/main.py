from fastapi import FastAPI
from app.blocklists import refresh_all_blocklists
from app.routers import auth, blocking, children, reports, qr_auth
from app.blocklists import is_domain_blocked


app = FastAPI(title="Al-Haris API", version="0.1.0")

# Include routers
app.include_router(auth.router)
app.include_router(blocking.router)
app.include_router(children.router)
app.include_router(reports.router)
app.include_router(qr_auth.router)


@app.on_event("startup")
def startup_event():
    print("Loading blocklists...")
    refresh_all_blocklists()
    print("Blocklists loaded!")
    assert is_domain_blocked("pornhub.com", ["adult"]), "Blocklist check failed!"
    print("Startup checks passed!")

@app.get("/")
def root():
    return {"message": "Hello Veil Citizens!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}