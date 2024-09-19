from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskSettings(BaseSettings):
    outbox_batch_size: int = 100
    outbox_publish_enabled: bool = True
    outbox_scan_interval: int = 5

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')


@cache
def get_task_settings() -> TaskSettings:
    return TaskSettings()
