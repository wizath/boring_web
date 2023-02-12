import os
from functools import lru_cache
from typing import Any, Dict, List

from dotenv import load_dotenv
from pydantic import BaseSettings

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(BaseSettings):
    HOST = '127.0.0.1'
    PORT = 8000
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = os.environ.get('SECRET_KEY', '41f62834-0071-11e6-a247-000ec6c2372c')
    DATABASE_URL: str = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///sqlite.db')
    TITLE: str = "Boring WEB"
    VERSION: str = "0.1"

    ALLOWED_HOSTS: List[str] = ["*"]

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "title": self.TITLE,
            "version": self.VERSION,
        }


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite+aiosqlite:///sqlite.db'


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


@lru_cache()
def get_settings():
    config_name = os.environ.get('APP_CONFIG', 'development')
    config_object = config.get(config_name, config['development'])
    return config_object()


settings = get_settings()
