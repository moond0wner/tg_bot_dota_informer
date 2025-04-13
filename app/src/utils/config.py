from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_HOST: str
    DB_PASSWORD: str

    model_config =  SettingsConfigDict(env_file="../../../.env") #../../../.env

settings = Settings()

