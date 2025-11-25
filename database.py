from tortoise import Tortoise
from config import settings

async def init_db():
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
