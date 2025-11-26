import asyncio
import json
from tortoise import Tortoise
from app import TORTOISE_CONFIG
import models  # Import the models module as 'models'
from models import TutorProfile, Resume, ParentReview # Explicitly import model classes
from config import settings
from datetime import datetime
from typing import List

async def load_fixtures_from_file(fixture_path: str):
    with open(fixture_path, 'r') as f:
        fixtures = json.load(f)

    # Dictionary to map fixture model names (lowercase) to actual model classes
    model_mapping = {
        "tutorprofile": TutorProfile,
        "resume": Resume,
        "parentreview": ParentReview,
    }

    for entry in fixtures:
        # Assume the entry is directly the model's data
        fields_to_create = entry.copy()
        pk = fields_to_create.pop("id", None) # Extract 'id' as primary key

        if pk is None:
            print(f"Entry missing 'id' field, skipping: {entry}")
            continue

        # Convert datetime strings to datetime objects
        for dt_field in ["created_at", "updated_at"]:
            if dt_field in fields_to_create and isinstance(fields_to_create[dt_field], str):
                try:
                    # Replace space with T to make it ISO 8601 compliant for fromisoformat
                    # Also handle potential 'Z' for UTC timezone indicator
                    fields_to_create[dt_field] = datetime.fromisoformat(fields_to_create[dt_field].replace('Z', '+00:00').replace(' ', 'T'))
                except ValueError:
                    print(f"Warning: Could not parse datetime string '{fields_to_create[dt_field]}' for {dt_field} (ID: {pk}), skipping conversion.")
        
        # Determine model class based on fields present in the entry
        model_cls = None
        if "student_crm_id" in fields_to_create and "is_verified" in fields_to_create and "content" in fields_to_create:
            model_cls = Resume
        elif "student_crm_id" in fields_to_create and "content" in fields_to_create:
            model_cls = ParentReview
        elif "username" in fields_to_create and "phone_number" in fields_to_create:
            # This case is for TutorProfile, if it were in this direct format
            model_cls = TutorProfile
        elif "phone_number" in fields_to_create and "branch" in fields_to_create:
            # This is for TutorProfile if username is removed and phone_number is direct
            model_cls = TutorProfile

        if model_cls is None:
            print(f"Could not determine model type for entry, skipping: {entry}")
            continue

        # Ensure is_verified is a boolean for Resume model
        if model_cls == Resume and "is_verified" in fields_to_create:
            fields_to_create["is_verified"] = bool(fields_to_create["is_verified"])

        # Special handling for TutorProfile to map 'username' from fixture to 'phone_number' in model
        if model_cls == TutorProfile:
            if "username" in fields_to_create and "phone_number" not in fields_to_create:
                fields_to_create["phone_number"] = fields_to_create.pop("username") # Use username from fixture as phone_number
            if "username" in fields_to_create: # If username still exists, remove it
                fields_to_create.pop("username")
            if "phone_number" not in fields_to_create or fields_to_create["phone_number"] is None:
                print(f"Error creating TutorProfile with ID {pk}: phone_number is missing or None, skipping.")
                continue

        # Check if entry with this primary key already exists
        if await model_cls.filter(id=pk).exists():
            print(f"{model_cls.__name__} with ID {pk} already exists, skipping.")
            continue
        
        try:
            await model_cls.create(id=pk, **fields_to_create)
            print(f"Created {model_cls.__name__} with ID {pk}")
        except Exception as e:
            print(f"Error creating {model_cls.__name__} with ID {pk}: {e}")

    print(f"Successfully processed fixtures from {fixture_path}")


async def load_all_fixtures(fixture_files: List[str]):
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    for fixture_file in fixture_files:
        await load_fixtures_from_file(fixture_file)

    await Tortoise.close_connections()
    print("All specified fixtures loaded.")


if __name__ == "__main__":
    # You might want to temporarily change the database URL to a test database if you don't want
    # to load fixtures into your main development database.
    # For this example, we'll use the default database defined in settings.
    
    fixture_files_to_load = [
        "fixtures/client_resumes.json",
        "fixtures/parent_review.json"
    ]
    asyncio.run(load_all_fixtures(fixture_files_to_load))
