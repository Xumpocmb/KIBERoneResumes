from fastapi import FastAPI
from typing import Optional

# Create admin app
admin_app = FastAPI(
    title="Admin Panel",
    description="Admin panel for managing KIBERone Resumes data",
    version="1.0.0"
)

@admin_app.get("/")
async def admin_home():
    return {"message": "Welcome to the Admin Panel"}

# In a real implementation, you would add admin routes for managing:
# - Tutor profiles
# - Resumes
# - Parent reviews
# With proper authentication and authorization
