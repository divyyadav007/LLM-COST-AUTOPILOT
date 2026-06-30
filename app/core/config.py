import logging
import os


class Settings:
    # Safely look up system runtime environments
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "MOCK_KEY_DEVELOPMENT")
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "MOCK_KEY_DEVELOPMENT")

    # Locate DB relative to workspace home to ensure write clearance profiles
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH: str = os.path.join(BASE_DIR, "app", "db", "autopilot.db")

    # Logging configuration settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


settings = Settings()


def setup_logging() -> None:
    """Configures system-wide standard logging structure."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO), format=settings.LOG_FORMAT
    )
