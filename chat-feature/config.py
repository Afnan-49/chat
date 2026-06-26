from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ---- App ----
    APP_NAME: str = "Beyn_test"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@localhost:5432/beyn_test"
    