from tortoise import Tortoise
from config import settings

TORTOISE_CONFIG = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()
