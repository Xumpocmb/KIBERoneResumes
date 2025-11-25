from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import models
import schemas
import auth
from crm_integration import (
    get_tutor_data_from_crm,
    get_client_data_from_crm,
    get_tutor_groups_from_crm,
    get_group_clients_from_crm
)

router = APIRouter()

# Tutor endpoints
@router.post("/tutors/register/", response_model=schemas.TutorProfileResponse)
async def register_tutor(
    tutor: schemas.TutorProfileCreate
):
    # Check if tutor with this username already exists
    existing_tutor = await auth.get_tutor_by_username(tutor.username)
    if existing_tutor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new tutor profile with hashed password
    db_tutor = await models.TutorProfile.create(
        username=tutor.username,
        tutor_crm_id=tutor.tutor_crm_id,
        tutor_name=tutor.tutor_name,
        branch=tutor.branch,
        is_senior=tutor.is_senior,
        hashed_password=auth.get_password_hash(tutor.password)  # Use password from request
    )
    
    return db_tutor


@router.post("/tutors/login/", response_model=schemas.Token)
async def login_tutor(
    tutor_login: schemas.TutorLogin
):
    tutor = await auth.authenticate_tutor(tutor_login.username, tutor_login.password)
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": tutor.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/tutors/groups/")
async def get_tutor_groups(
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    # Integrate with CRM to get tutor's groups
    if current_tutor.tutor_crm_id:
        groups_data = await get_tutor_groups_from_crm(current_tutor.tutor_crm_id)
        if groups_data:
            return groups_data
    
    # Fallback response if CRM integration fails
    return {"groups": []}


@router.get("/groups/clients/")
async def get_group_clients(
    group_id: str,  # Added group_id parameter
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    # Integrate with CRM to get group clients
    clients_data = await get_group_clients_from_crm(group_id)
    if clients_data:
        return clients_data
    
    # Fallback response if CRM integration fails
    return {"clients": []}


# Resume endpoints
@router.get("/resumes/client/", response_model=List[schemas.ResumeResponse])
async def get_client_resumes(
    student_crm_id: str,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    """Get resumes for a specific client."""
    resumes = await models.Resume.filter(student_crm_id=student_crm_id)
    return resumes


@router.post("/resumes/{resume_id}/", response_model=schemas.ResumeResponse)
async def update_resume(
    resume_id: int,
    resume_update: schemas.ResumeUpdate,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    """Update a specific resume."""
    resume = await models.Resume.get_or_none(id=resume_id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update the resume
    update_data = resume_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)
    
    await resume.save()
    return resume


@router.post("/resumes/{resume_id}/verify/", response_model=schemas.ResumeResponse)
async def verify_resume(
    resume_id: int,
    current_tutor: models.TutorProfile = Depends(auth.get_current_senior_tutor)
):
    """Verify a specific resume (requires senior tutor)."""
    resume = await models.Resume.get_or_none(id=resume_id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update the resume verification status
    resume.is_verified = True
    await resume.save()
    return resume


@router.get("/resumes/unverified/", response_model=List[schemas.ResumeResponse])
async def get_unverified_resumes(
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    """Get all unverified resumes."""
    resumes = await models.Resume.filter(is_verified=False)
    return resumes


@router.post("/resumes/", response_model=schemas.ResumeResponse)
async def create_resume(
    resume: schemas.ResumeCreate,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    """Create a new resume."""
    db_resume = await models.Resume.create(
        student_crm_id=resume.student_crm_id,
        content=resume.content,
        is_verified=resume.is_verified
    )
    
    return db_resume


@router.delete("/resumes/{resume_id}/")
async def delete_resume(
    resume_id: int,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    """Delete a specific resume."""
    resume = await models.Resume.get_or_none(id=resume_id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    await resume.delete()
    return {"message": "Resume deleted successfully"}


# Review endpoints
@router.get("/reviews/{student_crm_id}/", response_model=List[schemas.ParentReviewResponse])
async def get_parent_reviews(
    student_crm_id: str,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    """Get parent reviews for a specific student."""
    reviews = await models.ParentReview.filter(student_crm_id=student_crm_id)
    return reviews


# Client endpoints
@router.get("/clients/detail/")
async def get_client_detail(
    student_crm_id: str,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    # Integrate with CRM to get client details
    client_data = await get_client_data_from_crm(student_crm_id)
    if client_data:
        return client_data
    
    # Fallback response if CRM integration fails
    return {"client_detail": {}}
