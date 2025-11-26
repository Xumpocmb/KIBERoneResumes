from tortoise.models import Model
from tortoise import fields


class TutorProfile(Model):
    id = fields.IntField(pk=True)
    tutor_crm_id = fields.CharField(max_length=255, null=True, unique=True)
    tutor_name = fields.CharField(max_length=255, null=True)
    branch = fields.CharField(max_length=255, null=True)
    is_senior = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=20, unique=True)


class Resume(Model):
    id = fields.IntField(pk=True)
    student_crm_id = fields.CharField(max_length=255)
    content = fields.TextField(null=True)
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class ParentReview(Model):
    id = fields.IntField(pk=True)
    student_crm_id = fields.CharField(max_length=255)
    content = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
