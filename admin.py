from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import TutorProfile, Resume, ParentReview
import auth

router = APIRouter(dependencies=[Depends(auth.get_current_senior_tutor)])
templates = Jinja2Templates(directory="templates")

# --- TutorProfile Admin Routes ---
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

# --- Resume Admin Routes ---
@router.get("/resumes", response_class=HTMLResponse)
async def list_resumes(request: Request):
    resumes = await Resume.all()
    return templates.TemplateResponse("resumes.html", {"request": request, "resumes": resumes})

@router.post("/resumes", response_class=RedirectResponse)
async def add_resume(
    student_crm_id: str = Form(...),
    content: Optional[str] = Form(None),
    is_verified: bool = Form(False)
):
    await Resume.create(
        student_crm_id=student_crm_id,
        content=content,
        is_verified=is_verified
    )
    return RedirectResponse(url="/admin/resumes", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/resumes/{resume_id}/update", response_class=RedirectResponse)
async def update_resume(
    resume_id: int,
    student_crm_id: str = Form(...),
    content: Optional[str] = Form(None),
    is_verified: bool = Form(False)
):
    resume = await Resume.get_or_none(id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume.student_crm_id = student_crm_id
    resume.content = content
    resume.is_verified = is_verified
    resume.updated_at = datetime.utcnow()
    await resume.save()
    return RedirectResponse(url="/admin/resumes", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/resumes/{resume_id}/delete", response_class=RedirectResponse)
async def delete_resume(resume_id: int):
    resume = await Resume.get_or_none(id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    await resume.delete()
    return RedirectResponse(url="/admin/resumes", status_code=status.HTTP_303_SEE_OTHER)

# --- ParentReview Admin Routes ---
@router.get("/parent_reviews", response_class=HTMLResponse)
async def list_parent_reviews(request: Request):
    reviews = await ParentReview.all()
    return templates.TemplateResponse("parent_reviews.html", {"request": request, "reviews": reviews})

@router.post("/parent_reviews", response_class=RedirectResponse)
async def add_parent_review(
    student_crm_id: str = Form(...),
    content: Optional[str] = Form(None)
):
    await ParentReview.create(
        student_crm_id=student_crm_id,
        content=content
    )
    return RedirectResponse(url="/admin/parent_reviews", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/parent_reviews/{review_id}/update", response_class=RedirectResponse)
async def update_parent_review(
    review_id: int,
    student_crm_id: str = Form(...),
    content: Optional[str] = Form(None)
):
    review = await ParentReview.get_or_none(id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Parent Review not found")
    
    review.student_crm_id = student_crm_id
    review.content = content
    review.updated_at = datetime.utcnow()
    await review.save()
    return RedirectResponse(url="/admin/parent_reviews", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/parent_reviews/{review_id}/delete", response_class=RedirectResponse)
async def delete_parent_review(review_id: int):
    review = await ParentReview.get_or_none(id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Parent Review not found")
    await review.delete()
    return RedirectResponse(url="/admin/parent_reviews", status_code=status.HTTP_303_SEE_OTHER)
