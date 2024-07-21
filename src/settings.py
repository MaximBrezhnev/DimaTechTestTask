import os

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class ProjectSettings(BaseSettings):
    """
    Класс, представляющий собой конфигурацию проекта
    """

    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    SECRET_KEY: str

    APP_TITLE: str
    APP_HOST: str
    APP_PORT: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
        ),
        extra="ignore",
    )


project_settings = ProjectSettings()
