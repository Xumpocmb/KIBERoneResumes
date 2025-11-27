from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import models
import schemas
import auth
from crm_integration import (
    get_all_groups,
    get_tutor_data_from_crm,
    get_client_data_from_crm,
    get_tutor_groups_from_crm,
    get_group_clients_from_crm
)

router = APIRouter()


# Тестовый endpoint для проверки
@router.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Backend is working"}


# Ваши основные endpoints здесь
@router.get("/api/test")
async def test_endpoint():
    return {"message": "Hello from FastAPI"}


# Tutor endpoints
@router.post("/tutors/register/", response_model=schemas.TutorProfileResponse)
async def register_tutor(
    register_data: schemas.TutorRegisterRequest
):
    existing_phone_tutor = await auth.get_tutor_by_phone_number(register_data.phone_number)
    if existing_phone_tutor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    tutor_data = await get_tutor_data_from_crm(register_data.phone_number, register_data.tutor_branch_id)

    if not tutor_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found in CRM"
        )

    tutor_crm_id = tutor_data.get("id", None)
    tutor_name = tutor_data.get("name", None)

    db_tutor = await models.TutorProfile.create(
        tutor_crm_id=tutor_crm_id,
        tutor_name=tutor_name,
        branch=register_data.tutor_branch_id,
        is_senior=False,
        phone_number=register_data.phone_number
    )

    return db_tutor


@router.post("/tutors/login/", response_model=schemas.Token)
async def login_tutor(
    tutor_login: schemas.TutorLogin
):
    tutor = await auth.authenticate_tutor(tutor_login.phone_number)
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Since we don't have username, we'll use phone number as the subject
    access_token = auth.create_access_token(data={"sub": tutor.phone_number})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/tutors/groups/")
async def get_tutor_groups(
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    # Integrate with CRM to get tutor's groups
    if current_tutor.tutor_crm_id and current_tutor.branch:
        
        if current_tutor.is_senior:
            groups_data = await get_all_groups()
        else:
            groups_data = await get_tutor_groups_from_crm(current_tutor.tutor_crm_id, current_tutor.branch)
        if groups_data:
            return groups_data
    
    # Fallback response if CRM integration fails
    return {"groups": []}


@router.get("/groups/clients/")
async def get_group_clients(
    group_id: str,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    if current_tutor.branch:
        clients_data = await get_group_clients_from_crm(group_id, current_tutor.branch)
        if clients_data:
            return clients_data

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


# Tutor endpoints (additional)
@router.get("/tutors/detail/")
async def get_tutor_detail(
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    # Integrate with CRM to get tutor details
    if current_tutor.tutor_crm_id and current_tutor.branch:
        tutor_data = await get_tutor_data_from_crm(current_tutor.phone_number, current_tutor.branch)
        if tutor_data:
            tutor_data["is_senior"] = current_tutor.is_senior
            return tutor_data
    
    # Fallback response if CRM integration fails
    return {"tutor_detail": {"is_senior": current_tutor.is_senior}}


# Tutor Management Endpoints (for senior tutors)
@router.post("/tutors/{tutor_id}/promote-to-senior/", response_model=schemas.TutorProfileResponse)
async def promote_to_senior(
    tutor_id: int,
    current_senior_tutor: models.TutorProfile = Depends(auth.get_current_senior_tutor)
):
    """Promote a tutor to senior status (requires an existing senior tutor)."""
    tutor = await models.TutorProfile.get_or_none(id=tutor_id)
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    tutor.is_senior = True
    await tutor.save()
    return tutor


# Client endpoints
@router.get("/clients/detail/")
async def get_client_detail(
    student_crm_id: str,
    current_tutor: models.TutorProfile = Depends(auth.get_current_active_tutor)
):
    # Integrate with CRM to get client details
    if current_tutor.branch:
        client_data = await get_client_data_from_crm(student_crm_id, current_tutor.branch)
        if client_data:
            return client_data
    
    # Fallback response if CRM integration fails
    return {"client_detail": {}}
