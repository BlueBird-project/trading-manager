import argparse
import os
from typing import Optional, Tuple

if __name__ == "__main__":
    # ke_endpoint = os.environ.get( "KE_ENDPOINT")
    os.environ.setdefault("SERVICE_LOG_DIR", "d:/tmp/logs/")

from pydantic import BaseModel


class AppArgs(BaseModel):
    config_path: Optional[str]
    env: Optional[str] = None
    hash_pg_schema: bool = False

    @property
    def env_path(self) -> str:
        return self.env if self.env is not None else ".env"

    # hash_pg_schema: bool = False

    def __init__(self, args):
        super().__init__(**args)


def get_args() -> AppArgs:
    parser = argparse.ArgumentParser()
    # parser.add_argument('-d', '--debug', help='enable debug logs', action='store_true')
    parser.add_argument('-c', '--config-path', help='YAML config path', default='./resources/config.yaml')
    parser.add_argument('--env', help='env path', default='.env')
    parser.add_argument('--hash-pg-schema', help='generate db hash', default=False, action='store_true')
    # parser.add_argument('--hash-pg-schema', help='generate db hash', default=False, action='store_true')
    parsed_args = parser.parse_args()
    return AppArgs(args=parsed_args.__dict__)


class DemoArgs(BaseModel):
    country: str
    date: str
    type: str


def get_demo_args() -> Tuple[AppArgs, DemoArgs]:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-path', help='YAML config path', default='/config/config.yaml')
    parser.add_argument('--env', help='env path', default='/env/.env.tm.demo')
    parser.add_argument('--country', help='country', default='POLAND')
    parser.add_argument('--type', help='market type', default='INTRADAY')
    parser.add_argument('--date', '-d', help='date YYYY-MM-DD', )
    # parser.add_argument('--hash-pg-schema', help='generate db hash', default=False, action='store_true')
    parsed_args = parser.parse_args()
    return AppArgs(args=parsed_args.__dict__), DemoArgs(**parsed_args.__dict__)


app_args: Optional[AppArgs] = None


def init_args() -> AppArgs:
    global app_args
    app_args = get_args()
    return app_args


def init_demo_args() -> DemoArgs:
    global app_args
    app_args, demo_args = get_demo_args()
    return demo_args


def set_logging():
    global app_args
    from io import StringIO
    import logging.config
    from tm.core import app_settings

    with open(app_settings.logging_conf_path) as f:
        ini_text = os.path.expandvars(f.read())
        config_fp = StringIO(ini_text)
        logging.config.fileConfig(config_fp)
