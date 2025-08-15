import logging
from typing import Optional, Union

from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings


def setup_logging_console(
    *,
    level: Union[int, str],
) -> None:
    logger = logging.getLogger()
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    logger.addHandler(console_handler)


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


class Settings(BaseSettings):
    """
    Each setting is read from the corresponding environment variable.
    """

    bueze: BuezeConfig
    logging: Optional[LoggingConfig] = None

    class Config:
        env_nested_delimiter = "__"
        env_parse_none_str = "None"


settings = Settings()
