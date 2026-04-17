from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    POSTGRES_URL: str
    FALKORDB_HOST: str = "localhost"
    FALKORDB_PORT: int = 6379
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_API_KEY: str
    APP_ENV: str = "development"
    DEBUG: bool = False


settings = Settings()
