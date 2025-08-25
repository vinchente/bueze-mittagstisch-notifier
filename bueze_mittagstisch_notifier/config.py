from typing import Optional

from pydantic import BaseModel, SecretStr, model_validator
from pydantic_settings import BaseSettings


class ConsoleConfig(BaseModel):
    enabled: bool = True
    print_spans: bool = False


class LoggingConfig(BaseModel):
    console: Optional[ConsoleConfig] = None

    @model_validator(mode="after")
    def validate_model(self) -> "LoggingConfig":
        if not self.console:
            self.console = ConsoleConfig(enabled=True)

        return self


class BuezeConfig(BaseModel):
    page_url: str


class TelegramBotConfig(BaseModel):
    name: str
    token: SecretStr


class TelegramConfig(BaseModel):
    bot: TelegramBotConfig
    channel_id: int


class FilenamesStorageConfig(BaseModel):
    name: str


class Settings(BaseSettings):
    """
    Each setting is read from the corresponding environment variable.
    """

    bueze: BuezeConfig
    telegram: TelegramConfig
    logging: Optional[LoggingConfig] = None
    filenames_storage: FilenamesStorageConfig

    class Config:
        env_nested_delimiter = "__"
        env_parse_none_str = "None"


settings = Settings()
