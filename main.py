from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api
from database import init_db, close_db
from config import settings
from admin import router as admin_router # Import the new admin router

# Create FastAPI application
app = FastAPI(
    title="KIBERone Resumes API",
    description="API for managing tutor profiles, resumes, and parent reviews",
    version="1.0.0"
)

# Add CORS middleware
allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://kiber-resume.of.by",
    "https://kiber-resume.of.by",  # если есть HTTPS
    "http://localhost:3000",  # для разработки
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api.router, prefix="/api/v1")

# Include the custom admin router
app.include_router(admin_router, prefix="/admin")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
def read_root():
    return {"message": "KIBERone Resumes API"}
