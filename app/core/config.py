from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DivineAI"
    API_V1_STR: str = "/api/v1"
    
    UPLOAD_DIR: str = "media"          # local folder for uploaded/generated images
    BASE_URL: str = "http://localhost:8000"  # used to build public image URLs
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
