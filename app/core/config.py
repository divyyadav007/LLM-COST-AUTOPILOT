import os

class Settings:
    # Safely look up system runtime environments
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "MOCK_KEY_DEVELOPMENT")
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "MOCK_KEY_DEVELOPMENT")
    
    # Locate DB relative to workspace home to ensure write clearance profiles
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DB_PATH: str = os.path.join(BASE_DIR, "data", "autopilot.db")

settings = Settings()