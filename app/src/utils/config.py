from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_USER: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DB_PASSWORD: str
    ADMINS: int

    model_config = SettingsConfigDict()  # ../../../.env


settings = Settings()
