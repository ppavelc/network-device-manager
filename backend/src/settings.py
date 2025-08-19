from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    CREDENTIALS_COLLECTION: str
    KEYS_COLLECTION: str
    DEBUG: bool = False
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()