from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    database: str = 'db'
    user: str = 'user'
    password: str = 'password'
    host: str = 'localhost'
    port: int = 5432

    model_config = SettingsConfigDict(env_prefix='postgres_',
                                      env_file='.env',
                                      env_file_encoding='utf-8',
                                      extra='allow')

    @property
    def dsn(self) -> str:
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(**self.model_dump())


@cache
def get_db_settings() -> DbSettings:
    return DbSettings()
