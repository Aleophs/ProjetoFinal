from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    log_file: str = "logs/app.log"
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 5

settings = Settings()