from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Kept deliberately short: the refresh token lives in localStorage, so a
    # small window limits exposure if it is ever stolen (e.g. via XSS).
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()