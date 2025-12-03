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
@router.get("/health/")
async def health_check():
    return {"status": "ok", "message": "Backend is working"}


# Ваши основные endpoints здесь
@router.get("/test/")
async def test_endpoint():
    return {"message": "Hello from FastAPI"}


# Tutor endpoints
@router.post("/tutors/register/", response_model=schemas.TutorProfileResponse)
async def register_tutor(
    register_data: schemas.TutorRegisterRequest
):
    try:
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

        # Extract all fields from CRM data with proper error handling
        tutor_crm_id = tutor_data.get("id", None)
        tutor_name = tutor_data.get("name", None)
        branch_ids = tutor_data.get("branch_ids", None)
        dob = tutor_data.get("dob", None)
        gender = tutor_data.get("gender", None)
        streaming_id = tutor_data.get("streaming_id", None)
        note = tutor_data.get("note", None)
        e_date = tutor_data.get("e_date", None)
        avatar_url = tutor_data.get("avatar_url", None)
        phone = tutor_data.get("phone", None)
        email = tutor_data.get("email", None)
        web = tutor_data.get("web", None)
        addr = tutor_data.get("addr", None)
        teacher_to_skill = tutor_data.get("teacher-to-skill", None)

        # Validate required fields to avoid potential database errors
        if tutor_crm_id is not None:
            tutor_crm_id = int(tutor_crm_id) if str(tutor_crm_id).isdigit() else None

        # Create or update tutor profile with all CRM data
        db_tutor = await models.TutorProfile.create(
            tutor_crm_id=tutor_crm_id,
            tutor_name=tutor_name,
            branch=register_data.tutor_branch_id,
            is_senior=True,
            phone_number=register_data.phone_number,
            # Additional fields from CRM
            branch_ids=branch_ids,
            dob=dob,
            gender=gender,
            streaming_id=streaming_id,
            note=note,
            e_date=e_date,
            avatar_url=avatar_url,
            phone=phone,
            email=email,
            web=web,
            addr=addr,
            teacher_to_skill=teacher_to_skill
        )

        return db_tutor
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while registering tutor: {str(e)}"
        )


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

    # Get updated tutor data from CRM and update DB record
    if tutor.branch:
        tutor_data = await get_tutor_data_from_crm(tutor.phone_number, tutor.branch)
        if tutor_data:
            # Update tutor profile with latest CRM data
            update_data = {}
            update_data["tutor_crm_id"] = tutor_data.get("id")
            update_data["tutor_name"] = tutor_data.get("name")
            update_data["branch_ids"] = tutor_data.get("branch_ids")
            update_data["dob"] = tutor_data.get("dob")
            update_data["gender"] = tutor_data.get("gender")
            update_data["streaming_id"] = tutor_data.get("streaming_id")
            update_data["note"] = tutor_data.get("note")
            update_data["e_date"] = tutor_data.get("e_date")
            update_data["avatar_url"] = tutor_data.get("avatar_url")
            update_data["phone"] = tutor_data.get("phone")
            update_data["email"] = tutor_data.get("email")
            update_data["web"] = tutor_data.get("web")
            update_data["addr"] = tutor_data.get("addr")
            update_data["teacher_to_skill"] = tutor_data.get("teacher-to-skill")

            # Update the tutor record with new CRM data
            for field, value in update_data.items():
                setattr(tutor, field, value)

            await tutor.save()

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
    # Return tutor details from the local database
    return {
        "id": current_tutor.tutor_crm_id,
        "name": current_tutor.tutor_name,
        "branch_ids": current_tutor.branch_ids,
        "branch": current_tutor.branch,
        "dob": current_tutor.dob,
        "gender": current_tutor.gender,
        "streaming_id": current_tutor.streaming_id,
        "note": current_tutor.note,
        "e_date": current_tutor.e_date,
        "avatar_url": current_tutor.avatar_url,
        "phone": current_tutor.phone,
        "email": current_tutor.email,
        "web": current_tutor.web,
        "addr": current_tutor.addr,
        "teacher-to-skill": current_tutor.teacher_to_skill,
        "is_senior": current_tutor.is_senior
    }


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


# Group endpoints
@router.get("/groups/sync/", response_model=dict)
async def sync_all_groups(
    current_tutor: models.TutorProfile = Depends(auth.get_current_senior_tutor)
):
    """
    Fetch all groups from CRM and synchronize them with the database
    Available only to senior tutors
    """
    try:
        groups_data = await get_all_groups()
        if not groups_data:
            return {"message": "No groups found in CRM", "synced_count": 0}

        synced_count = 0
        for group_data in groups_data:
            # Extract fields from CRM data
            crm_group_id = group_data.get("id")
            branch_ids = group_data.get("branch_ids")
            teacher_ids = group_data.get("teacher_ids")
            name = group_data.get("name")
            level_id = group_data.get("level_id")
            status_id = group_data.get("status_id")
            company_id = group_data.get("company_id")
            streaming_id = group_data.get("streaming_id")
            limit = group_data.get("limit")
            note = group_data.get("note")
            b_date = group_data.get("b_date")
            e_date = group_data.get("e_date")
            created_at = group_data.get("created_at")
            updated_at = group_data.get("updated_at")
            custom_aerodromnaya = group_data.get("custom_aerodromnaya")

            # Try to get existing group or create new one
            group, created = await models.Group.get_or_create(
                crm_group_id=crm_group_id,
                defaults={
                    "branch_ids": branch_ids,
                    "teacher_ids": teacher_ids,
                    "name": name,
                    "level_id": level_id,
                    "status_id": status_id,
                    "company_id": company_id,
                    "streaming_id": streaming_id,
                    "limit": limit,
                    "note": note,
                    "b_date": b_date,
                    "e_date": e_date,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "custom_aerodromnaya": custom_aerodromnaya
                }
            )

            # If the group already existed, update its fields
            if not created:
                group.branch_ids = branch_ids
                group.teacher_ids = teacher_ids
                group.name = name
                group.level_id = level_id
                group.status_id = status_id
                group.company_id = company_id
                group.streaming_id = streaming_id
                group.limit = limit
                group.note = note
                group.b_date = b_date
                group.e_date = e_date
                group.created_at = created_at
                group.updated_at = updated_at
                group.custom_aerodromnaya = custom_aerodromnaya
                await group.save()

            synced_count += 1

        return {"message": f"Successfully synchronized {synced_count} groups", "synced_count": synced_count}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while synchronizing groups: {str(e)}"
        )
