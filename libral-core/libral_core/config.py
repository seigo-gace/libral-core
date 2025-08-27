"""
Configuration management with GPG-encrypted .env files
Implements privacy-first configuration handling
"""

import os
from pathlib import Path
from typing import Optional

import gnupg
from pydantic import Field
from pydantic_settings import BaseSettings
import structlog

logger = structlog.get_logger(__name__)

class GPGConfigManager:
    """GPG-based encrypted configuration manager"""
    
    def __init__(self, gnupg_home: Optional[str] = None):
        self.gpg_home = gnupg_home or os.path.expanduser("~/.gnupg")
        self.gpg = gnupg.GPG(gnupghome=self.gpg_home)
        
    def decrypt_env_file(self, env_gpg_path: str) -> dict[str, str]:
        """Decrypt .env.gpg file and return environment variables"""
        try:
            with open(env_gpg_path, 'rb') as f:
                decrypted_data = self.gpg.decrypt_file(f)
                
            if not decrypted_data.ok:
                raise ValueError(f"GPG decryption failed: {decrypted_data.stderr}")
                
            # Parse decrypted .env content
            env_vars = {}
            for line in str(decrypted_data).strip().split('\n'):
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
                    
            logger.info("GPG configuration decrypted successfully", 
                       vars_count=len(env_vars))
            return env_vars
            
        except Exception as e:
            logger.error("Failed to decrypt GPG configuration", error=str(e))
            raise
            
    def encrypt_env_file(self, env_dict: dict[str, str], 
                        output_path: str, recipient: str) -> bool:
        """Encrypt environment variables to .env.gpg file"""
        try:
            # Format as .env content
            env_content = '\n'.join([f"{k}={v}" for k, v in env_dict.items()])
            
            encrypted_data = self.gpg.encrypt(
                env_content, 
                recipients=[recipient],
                armor=False
            )
            
            if not encrypted_data.ok:
                raise ValueError(f"GPG encryption failed: {encrypted_data.stderr}")
                
            with open(output_path, 'wb') as f:
                f.write(encrypted_data.data)
                
            logger.info("Configuration encrypted to GPG file", 
                       output_path=output_path)
            return True
            
        except Exception as e:
            logger.error("Failed to encrypt configuration", error=str(e))
            return False

class LibralSettings(BaseSettings):
    """Core configuration settings with GPG support"""
    
    # App Configuration
    app_name: str = Field(default="Libral Core", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database Configuration
    database_url: str = Field(env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    # Security Configuration
    secret_key: str = Field(env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    
    # GPG Configuration
    gpg_home: Optional[str] = Field(default=None, env="GPG_HOME")
    gpg_system_key_id: str = Field(env="GPG_SYSTEM_KEY_ID")
    gpg_passphrase: Optional[str] = Field(default=None, env="GPG_PASSPHRASE")
    
    # Telegram Configuration
    telegram_bot_token: str = Field(env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(env="TELEGRAM_WEBHOOK_SECRET")
    telegram_webhook_url: str = Field(env="TELEGRAM_WEBHOOK_URL")
    
    # Data Retention Policy (Privacy-First)
    temp_cache_retention_hours: int = Field(default=24, env="TEMP_CACHE_RETENTION_HOURS")
    user_data_encryption_required: bool = Field(default=True, env="USER_DATA_ENCRYPTION_REQUIRED")
    central_logging_disabled: bool = Field(default=True, env="CENTRAL_LOGGING_DISABLED")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def load_settings() -> LibralSettings:
    """Load settings with GPG support"""
    
    # Check for .env.gpg first
    env_gpg_path = Path(".env.gpg")
    if env_gpg_path.exists():
        logger.info("Loading GPG-encrypted configuration")
        gpg_manager = GPGConfigManager()
        env_vars = gpg_manager.decrypt_env_file(str(env_gpg_path))
        
        # Set environment variables from decrypted content
        for key, value in env_vars.items():
            os.environ[key] = value
            
    # Load settings (will use decrypted env vars or fallback to .env)
    return LibralSettings()

# Global settings instance
settings = load_settings()