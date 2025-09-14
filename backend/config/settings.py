"""
Configuration settings for Source AI MVP backend services.
This file contains shared configuration that can be used across all microservices.
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    url: str = "postgresql://user:password@localhost:5432/source_ai_mvp"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    
    @validator("url")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Database URL must be a PostgreSQL connection string")
        return v
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    
    url: str = "redis://localhost:6379/0"
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 10
    
    class Config:
        env_prefix = "REDIS_"


class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Password settings
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special_chars: bool = False
    
    class Config:
        env_prefix = "SECURITY_"


class FileUploadSettings(BaseSettings):
    """File upload configuration settings"""
    
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = ["jpg", "jpeg", "png", "gif", "webp"]
    upload_dir: str = "uploads"
    create_thumbnails: bool = True
    thumbnail_sizes: list = [(150, 150), (300, 300)]
    
    class Config:
        env_prefix = "UPLOAD_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings"""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    class Config:
        env_prefix = "LOG_"


class APISettings(BaseSettings):
    """API configuration settings"""
    
    title: str = "Source AI MVP API"
    description: str = "Microservices API for Source AI MVP"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_prefix = "API_"


class EnvironmentSettings(BaseSettings):
    """Environment configuration settings"""
    
    environment: str = "development"
    debug: bool = True
    testing: bool = False
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("debug", pre=True)
    def set_debug(cls, v, values):
        if "environment" in values and values["environment"] == "production":
            return False
        return v
    
    class Config:
        env_prefix = "ENV_"


class Settings:
    """Main settings class that combines all configuration sections"""
    
    def __init__(self):
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.security = SecuritySettings()
        self.file_upload = FileUploadSettings()
        self.logging = LoggingSettings()
        self.api = APISettings()
        self.environment = EnvironmentSettings()
    
    @property
    def is_development(self) -> bool:
        return self.environment.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.environment.testing


# Global settings instance
settings = Settings()


# Service-specific settings
class UsersServiceSettings(Settings):
    """Users service specific settings"""
    
    def __init__(self):
        super().__init__()
        self.api.title = "Users Service"
        self.api.description = "User management microservice"


class PhotosServiceSettings(Settings):
    """Photos service specific settings"""
    
    def __init__(self):
        super().__init__()
        self.api.title = "Photos Service"
        self.api.description = "Photo management microservice"


# Export commonly used settings
def get_database_url() -> str:
    """Get database URL from environment or settings"""
    return os.getenv("DATABASE_URL", settings.database.url)


def get_redis_url() -> str:
    """Get Redis URL from environment or settings"""
    return os.getenv("REDIS_URL", settings.redis.url)


def get_secret_key() -> str:
    """Get secret key from environment or settings"""
    return os.getenv("SECRET_KEY", settings.security.secret_key)


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return settings.environment.debug


def get_upload_dir() -> str:
    """Get upload directory path"""
    return settings.file_upload.upload_dir
