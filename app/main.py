from fastapi import FastAPI

app = FastAPI(title="Al-Haris API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Hello Veil Citizens!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}