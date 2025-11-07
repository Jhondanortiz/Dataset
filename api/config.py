from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "vulnerabilities_db"

    model_config = {"env_file": ".env"}

settings = Settings()