from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POST_USER: str
    POST_PASS: str
    POST_DB: str
    POST_PORT: str
    POST_HOST: str = "localhost"
    SECRET_KEY: str
    ALGORITHM_TOK: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()