from turtle import st
from dotenv import dotenv_values
from pydantic import BaseSettings

config = dotenv_values(".env")


class Settings(BaseSettings):
    # TODO change secret key to environment variable
    SECRET_KEY: str = "s3cr3t"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    PROJECT_NAME: str = "Sales Automation"

    # maximum upload size (200MB)
    MAX_FILE_SIZE: int = 200 * 1024 * 1024

    # maximum number of rows in CSV file (1 million)
    MAX_NUMBER_OF_ROWS: int = 1000000

    # CSV file store
    CSV_FILES_PATH: str = config.get("CSV_FILES_PATH")

    # Allowed mime-types
    ALLOWED_MIME_TYPES: set = {"text/csv", "text/plain"}

    class Config:
        case_sensitive = True


settings = Settings()
