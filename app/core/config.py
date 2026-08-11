from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DivineAI"
    API_V1_STR: str = "/api/v1"
    
    UPLOAD_DIR: str = "media"          # local folder for uploaded/generated images
    BASE_URL: str = "http://localhost:8000"  # used to build public image URLs
    GEMINI_API_KEY: Optional[str] = None
    
    # DB configuration (default values for local docker-compose setup)
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgrespassword"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "divineai"
    DATABASE_URL: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        
        import urllib.parse
        user = self.DB_USER or ""
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD or "")
        host = self.DB_HOST or "localhost"
        port = self.DB_PORT or "5432"
        name = self.DB_NAME or "divineai"
        
        # If DB_HOST contains a colon (like a GCP instance connection name) or points to a path
        if ":" in host or host.startswith("/"):
            return f"postgresql+psycopg2://{user}:{encoded_password}@/{name}?host=/cloudsql/{host}"
            
        return f"postgresql://{user}:{encoded_password}@{host}:{port}/{name}"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

