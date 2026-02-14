from typing import Optional, List
from zoneinfo import ZoneInfo

from effi_onto_tools.utils import DictBaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from tm import app_args

__TIME_ZONE__ = ZoneInfo("Europe/Warsaw")


class APPSettings(DictBaseSettings):
    logging_conf_path: str = Field(default="./resources/logging.ini")
    use_scheduler: bool = Field(default=False)
    use_rest_api: bool = Field(default=True)
    use_ke_api: bool = Field(default=False)
    # logging_out_path: str = Field(default="./resources/logging.ini")
    # ke_config_path: str = Field(default="./resources/ke_config.yaml")
    country_list: List[str] = Field(default=[])
    model_config = SettingsConfigDict(env_prefix='APP_', env_file=DictBaseSettings.env_path(),
                                      env_file_encoding="utf-8")

    @property
    def country_list_upper(self) -> List[str]:
        return [c.upper() for c in self.country_list]

    @classmethod
    def load(cls, **kwargs):
        return super().load(app_args.config_path, "APP".lower())


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


app_settings: APPSettings = APPSettings.load()
service_settings: ServiceSettings = ServiceSettings.load()
