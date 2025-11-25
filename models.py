from tortoise.models import Model
from tortoise import fields
from datetime import datetime

class TutorProfile(Model):
    id = fields.IntField(pk=True)
    tutor_crm_id = fields.CharField(max_length=255, null=True, unique=True)
    tutor_name = fields.CharField(max_length=255, null=True)
    branch = fields.CharField(max_length=255, null=True)  # This could be a foreign key to a Branch model if needed
    is_senior = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=20, unique=True)  # Phone number for authentication


class Resume(Model):
    id = fields.IntField(pk=True)
    student_crm_id = fields.CharField(max_length=255)
    content = fields.TextField(null=True)  # Up to 5000 characters will be validated at the application level
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class ParentReview(Model):
    id = fields.IntField(pk=True)
    student_crm_id = fields.CharField(max_length=255)
    content = fields.TextField(null=True)  # Up to 5000 characters will be validated at the application level
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
