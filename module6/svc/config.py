"""Configuration management using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/configservice",
        description="PostgreSQL database URL"
    )
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="configservice", description="Database name")
    db_user: str = Field(default="user", description="Database user")
    db_password: str = Field(default="password", description="Database password")
    db_pool_min_conn: int = Field(default=1, description="Minimum database connections")
    db_pool_max_conn: int = Field(default=20, description="Maximum database connections")

    # Application configuration
    log_level: str = Field(default="INFO", description="Logging level")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"  # Allow additional fields to support docker-compose environment variables
    }


# Global settings instance
settings = Settings()