from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BuezeConfig(BaseModel):
    page_url: str


class Settings(BaseSettings):
    """
    Each setting is read from the corresponding environment variable.
    """

    bueze: BuezeConfig

    class Config:
        env_nested_delimiter = "__"
        env_parse_none_str = "None"


settings = Settings()
