from typing import Optional
from effi_onto_tools.utils import DictBaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from tm import app_args


class ServiceSettings(DictBaseSettings):
    port: int = Field(default=8080)
    host: str = Field(default="0.0.0.0")
    root_path: str = Field(default="/")
    name: Optional[str] = Field(default="DEFAULT_SERVICE")
    model_config = SettingsConfigDict(env_prefix='SERVICE_', env_file=DictBaseSettings.env_path(),
                                      env_file_encoding="utf-8")

    @classmethod
    def load(cls, **kwargs):
        return super().load(app_args.config_path, "SERVICE".lower())


settings: ServiceSettings = ServiceSettings.load()
