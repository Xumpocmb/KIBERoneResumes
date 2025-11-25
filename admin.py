from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import TutorProfile
from typing import Optional
import auth # For hashing phone numbers if needed, or just direct comparison

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tutor_profiles", response_class=HTMLResponse)
async def list_tutor_profiles(request: Request):
    tutors = await TutorProfile.all()
    return templates.TemplateResponse("tutor_profiles.html", {"request": request, "tutors": tutors})

@router.post("/tutor_profiles", response_class=RedirectResponse)
async def add_tutor_profile(
    phone_number: str = Form(...),
    tutor_crm_id: Optional[str] = Form(None),
    tutor_name: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    is_senior: bool = Form(False)
):
    existing_tutor = await TutorProfile.get_or_none(phone_number=phone_number)
    if existing_tutor:
        raise HTTPException(status_code=400, detail="Tutor with this phone number already exists")
    
    await TutorProfile.create(
        phone_number=phone_number,
        tutor_crm_id=tutor_crm_id,
        tutor_name=tutor_name,
        branch=branch,
        is_senior=is_senior
    )
    return RedirectResponse(url="/admin/tutor_profiles", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/tutor_profiles/{tutor_id}/update", response_class=RedirectResponse)
async def update_tutor_profile(
    tutor_id: int,
    phone_number: str = Form(...),
    tutor_crm_id: Optional[str] = Form(None),
    tutor_name: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    is_senior: bool = Form(False)
):
    tutor = await TutorProfile.get_or_none(id=tutor_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    # Check if phone number is being changed to an existing one
    if tutor.phone_number != phone_number:
        existing_tutor_with_new_phone = await TutorProfile.get_or_none(phone_number=phone_number)
        if existing_tutor_with_new_phone and existing_tutor_with_new_phone.id != tutor_id:
            raise HTTPException(status_code=400, detail="Phone number already in use by another tutor")

    tutor.phone_number = phone_number
    tutor.tutor_crm_id = tutor_crm_id
    tutor.tutor_name = tutor_name
    tutor.branch = branch
    tutor.is_senior = is_senior
    await tutor.save()
    return RedirectResponse(url="/admin/tutor_profiles", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/tutor_profiles/{tutor_id}/delete", response_class=RedirectResponse)
async def delete_tutor_profile(tutor_id: int):
    tutor = await TutorProfile.get_or_none(id=tutor_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    await tutor.delete()
    return RedirectResponse(url="/admin/tutor_profiles", status_code=status.HTTP_303_SEE_OTHER)
