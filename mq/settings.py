import urllib.parse
from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class MqSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 5672
    virtual_host: str = 'main'
    username: str = 'user'
    password: str = 'pass'
    qos_prefetch_count: int = 1
    heartbeat: int = 60
    publisher_retry_attempts: int = 5

    # output
    fencing_indicators_ex: str = 'fencing-indicators-ex'

    model_config = SettingsConfigDict(env_prefix='mq_', env_file='mq.env', env_file_encoding='utf-8')

    @property
    def dsn(self) -> str:
        return (f'amqp://{self.username}:{self.password}@{self.host}:{self.port}/'
                f'{urllib.parse.quote_plus(self.virtual_host)}?heartbeat={self.heartbeat}')


@cache
def get_mq_settings() -> MqSettings:
    return MqSettings()
