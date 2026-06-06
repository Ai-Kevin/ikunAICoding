from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoTest Pro"
    API_V1_PREFIX: str = "/api/v1"

    # JWT
    SECRET_KEY: str = "autotest-pro-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "sqlite:///./autotest.db"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
