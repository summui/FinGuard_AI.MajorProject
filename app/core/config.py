# Application settings and environment variable management using Pydantic Settings

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    gemini_api_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()