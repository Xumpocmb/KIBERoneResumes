from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "parentreview" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "student_crm_id" VARCHAR(255) NOT NULL,
    "content" TEXT,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "resume" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "student_crm_id" VARCHAR(255) NOT NULL,
    "content" TEXT,
    "is_verified" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "tutorprofile" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "tutor_crm_id" VARCHAR(255) UNIQUE,
    "tutor_name" VARCHAR(255),
    "branch" VARCHAR(255),
    "is_senior" INT NOT NULL DEFAULT 0,
    "hashed_password" VARCHAR(255) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_tutorprofil_usernam_15e5c4" ON "tutorprofile" ("username");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmO9P4jAYx/8Vwisu8Yxy/sq9A+VOLgIG553RmKVshTVu7Ww7kRj/92u7zW5jLMyggu"
    "7deH7Q5/n02fZdn+oesaHLts8BhZgP4QOC0/rP2lMdAw+Ki1z/Vq0OfF97pYGDkasSfBVJ"
    "deSIcQosLnxj4DIoTDZkFkU+RwQLKw5cVxqJJQIRnmhTgNF9AE1OJpA7kArHza0wI2zDR8"
    "jin/6dOUbQtVNlI1uurewmn/nK1sX8lwqUq41Mi7iBh3WwP+MOwS/RCHNpnUAMKeBQ/j2n"
    "gSxfVhd1G3cUVqpDwhITOTYcg8DliXaXZGARLPmJaphqcCJX+d7c3TvcO/pxsHckQlQlL5"
    "bD57A93XuYqAj0jfqz8gMOwgiFUXNjPLDF9pkW9cw8hscOoPkQ5zMzQEUbWaAxviKisUEj"
    "1WO0IqYeeDRdiCfckSD39wsI/m0Nj09bw4aI+ia7IWK0w7nvR65m6JOYNVaxIofhQKV5Gv"
    "BxwVAmUl4FMhq8d+RYgM3oXBmyZo+xezdJq9FrXSmQ3izynA36v+PwBN3js0E7C5VC2b4J"
    "crieCA9HHlzANpWZwWtHqdvxxZpOrejBHmB3Fu11Ef1ur3NhtHrnqS04aRkd6Wmm8MfWxk"
    "Fmvl/+pPava5zW5M/a9aDfUQQJ4xOqVtRxxnVd1gQCTkxMpiawE8/D2BqDSW1s4Nuv3Nh0"
    "ZrWxH7qxqnj5hh7fJd410jAC1t0UUNuc85AmWRQ77/KaXtYCMJioXZFsZZWRfhlCFqjhml"
    "M2kadQ01AdU6mZSs1UaqZSMytXM4iZD5AisV7OoLYJcSHAC274dGaG70ikvtWkln0ELo+4"
    "PRicpRC3u1mGl712Z9jYVbxFEOIw+VCoZOInUxOVTPykG7tOMtEQZdFzSsbIzRWLKX+hZO"
    "Qy0k9EVsJxg4RjwCBV1yUkYzJnNWLxzSm+vVRUt8Er9Hc2byWi8dPwLDua6awNEeDvQHNE"
    "AbacMiR1RkUx8eXCIEaElv9u0XnVV0saqgOYIxSqDxibElrq2ZmT+sUPL9ZEXbbEV7rl1H"
    "N0ZeQpVJRAx1RacoO05AOkTJZU4g5OpHzxOzf5SJS3RgmIUfhmAtzd2VkCoIhaCFD5ljy3"
    "/XMx6Jc9t70Ub258YyOLb9VcxPjtemItoCi7Lj7GzZ7YbqWPOuQftD/69fL8HzwCcIw="
)
