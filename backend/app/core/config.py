from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hospital Operations Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./hospital.db"
    
    # Operational Thresholds
    EMERGENCY_OVERCROWDING_THRESHOLD: float = 0.85  # 85% capacity triggers alert
    STAFFED_ICU_RATIO: float = 1.0  # 1 nurse per 1 ICU patient
    STAFFED_GENERAL_RATIO: float = 4.0  # 1 nurse per 4 General ward patients
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

