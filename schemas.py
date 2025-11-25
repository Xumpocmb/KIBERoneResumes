from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# TutorProfile Schemas
class TutorProfileBase(BaseModel):
    tutor_crm_id: Optional[str] = None
    tutor_name: Optional[str] = None
    branch: Optional[str] = None
    is_senior: bool = False


class TutorProfileCreate(TutorProfileBase):
    phone_number: str  # Phone number for authentication


class TutorRegisterRequest(BaseModel):
    phone_number: str  # phone number for authentication
    tutor_branch_id: str  # branch_id from the front-end


class TutorProfileUpdate(BaseModel):
    tutor_crm_id: Optional[str] = None
    tutor_name: Optional[str] = None
    branch: Optional[str] = None
    is_senior: Optional[bool] = None


class TutorProfileResponse(TutorProfileBase):
    id: int

    class Config:
        from_attributes = True


# Resume Schemas
class ResumeBase(BaseModel):
    student_crm_id: str
    content: Optional[str] = Field(None, max_length=5000)
    is_verified: bool = False


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=5000)
    is_verified: Optional[bool] = None


class ResumeResponse(ResumeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ParentReview Schemas
class ParentReviewBase(BaseModel):
    student_crm_id: str
    content: Optional[str] = Field(None, max_length=5000)


class ParentReviewCreate(ParentReviewBase):
    pass


class ParentReviewUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=5000)


class ParentReviewResponse(ParentReviewBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    phone_number: Optional[str] = None


class TutorLogin(BaseModel):
    phone_number: str
