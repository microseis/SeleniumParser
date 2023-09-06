from pydantic.v1 import BaseSettings


class AppSettings(BaseSettings):
    """Настройки приложения."""

    category: str = "category"
    num_pages: int = 0
    website_name: str = "website"

    class Config:
        env_file = "../.env"


app_settings = AppSettings()
