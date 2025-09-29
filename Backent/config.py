from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POST_USER: str
    POST_PASS: str
    POST_DB: str
    POST_PORT: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
