from tortoise.models import Model
from tortoise import fields


class TutorProfile(Model):
    id = fields.IntField(pk=True)
    tutor_crm_id = fields.CharField(max_length=255, null=True, unique=True)
    tutor_name = fields.CharField(max_length=255, null=True)
    branch = fields.CharField(max_length=255, null=True)
    is_senior = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=20, unique=True)

    # Additional fields based on CRM response
    branch_ids = fields.JSONField(null=True)  # Corresponds to "branch_ids" in the JSON
    dob = fields.CharField(max_length=10, null=True)  # Corresponds to "dob" in the JSON
    gender = fields.IntField(null=True)  # Corresponds to "gender" in the JSON
    streaming_id = fields.IntField(null=True)  # Corresponds to "streaming_id" in the JSON
    note = fields.TextField(null=True)  # Corresponds to "note" in the JSON
    e_date = fields.CharField(max_length=10, null=True)  # Corresponds to "e_date" in the JSON
    avatar_url = fields.CharField(max_length=500, null=True)  # Corresponds to "avatar_url" in the JSON
    phone = fields.JSONField(null=True)  # Corresponds to "phone" array in the JSON
    email = fields.JSONField(null=True)  # Corresponds to "email" array in the JSON
    web = fields.JSONField(null=True)  # Corresponds to "web" array in the JSON
    addr = fields.JSONField(null=True)  # Corresponds to "addr" array in the JSON
    teacher_to_skill = fields.JSONField(null=True)  # Corresponds to "teacher-to-skill" in the JSON


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


class Group(Model):
    id = fields.IntField(pk=True)
    crm_group_id = fields.IntField(unique=True)  # Corresponds to "id" in the JSON
    branch_ids = fields.JSONField()  # Corresponds to "branch_ids" in the JSON
    teacher_ids = fields.JSONField()  # Corresponds to "teacher_ids" in the JSON
    name = fields.CharField(max_length=500)  # Corresponds to "name" in the JSON
    level_id = fields.IntField()  # Corresponds to "level_id" in the JSON
    status_id = fields.IntField()  # Corresponds to "status_id" in the JSON
    company_id = fields.IntField(null=True)  # Corresponds to "company_id" in the JSON
    streaming_id = fields.IntField(null=True)  # Corresponds to "streaming_id" in the JSON
    limit = fields.IntField()  # Corresponds to "limit" in the JSON
    note = fields.TextField(null=True)  # Corresponds to "note" in the JSON
    b_date = fields.CharField(max_length=10, null=True)  # Corresponds to "b_date" in the JSON
    e_date = fields.CharField(max_length=10, null=True)  # Corresponds to "e_date" in the JSON
    created_at = fields.CharField(max_length=20, null=True)  # Corresponds to "created_at" in the JSON
    updated_at = fields.CharField(max_length=20, null=True)  # Corresponds to "updated_at" in the JSON
    custom_aerodromnaya = fields.CharField(max_length=10, null=True)  # Corresponds to "custom_aerodromnaya" in the JSON

    # Relationship to tutors (many-to-many through a separate model if needed)
    tutors = fields.ManyToManyField('models.TutorProfile', related_name='groups', null=True)
