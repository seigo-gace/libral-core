"""
Configuration settings for Libral Core
"""

from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Global configuration settings"""
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # Database
    database_url: str = Field(default="postgresql://localhost:5432/libral_core")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # GPG Configuration
    gpg_home: str = Field(default="~/.gnupg")
    gpg_system_key_id: Optional[str] = Field(default=None)
    gpg_passphrase: Optional[str] = Field(default=None)
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    
    # External APIs
    telegram_bot_token: Optional[str] = Field(default=None)
    telegram_webhook_secret: Optional[str] = Field(default=None)
    
    # Payment Configuration
    stripe_secret_key: Optional[str] = Field(default=None)
    stripe_webhook_secret: Optional[str] = Field(default=None)
    paypal_client_id: Optional[str] = Field(default=None)
    paypal_client_secret: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()