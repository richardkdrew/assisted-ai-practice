"""Application settings and configuration management."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_db: str
    database_user: str
    database_password: str
    database_url: str
    database_test_url: str

    # Application Configuration
    log_level: str = "INFO"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Connection Pool Settings
    db_min_connections: int = 1
    db_max_connections: int = 20

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
