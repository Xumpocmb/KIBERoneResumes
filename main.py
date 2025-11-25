from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api
from database import init_db, close_db
from admin import admin_app
from config import settings

# Create FastAPI application
app = FastAPI(
    title="KIBERone Resumes API",
    description="API for managing tutor profiles, resumes, and parent reviews",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api.router, prefix="/api/v1")

# Include admin panel
app.mount("/admin", admin_app)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
def read_root():
    return {"message": "KIBERone Resumes API"}
