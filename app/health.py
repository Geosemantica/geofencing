from functools import wraps
from typing import Type
import aio_pika

from fastapi_healthchecks.api.router import HealthcheckRouter, Probe, Check, CheckResult
from fastapi_healthchecks.checks.postgres import PostgreSqlCheck

from dal.settings import get_db_settings
from mq.settings import get_mq_settings


def supress_tb(cls: Type[Check]):
    @wraps(cls, updated=())
    class SilentCheck(cls):
        async def __call__(self):
            res: CheckResult = await super().__call__()
            if res.details:
                res.details = 'Connection failed'
            return res

    return SilentCheck


class RabbitMqCheck(Check):
    def __init__(self, dsn: str):
        self.dsn = dsn

    async def __call__(self) -> CheckResult:
        try:
            async with await aio_pika.connect_robust(
                    self.dsn
            ):
                return CheckResult(name='RabbitMq', passed=True)
        except Exception as exception:
            return CheckResult(name='RabbitMq', passed=False, details=str(exception))


class ReadinessCheck(Check):
    async def __call__(self, *args, **kwargs) -> CheckResult:
        return CheckResult(name='Initialization', passed=True)


def get_router() -> HealthcheckRouter:
    return HealthcheckRouter(
        Probe(
            name='readiness',
            checks=[ReadinessCheck()]
        ),
        Probe(
            name='liveness',
            checks=[supress_tb(PostgreSqlCheck).from_url(get_db_settings().dsn),
                    RabbitMqCheck(get_mq_settings().dsn)]
        ),
        Probe(
            name='health',
            checks=[supress_tb(PostgreSqlCheck).from_url(get_db_settings().dsn),
                    RabbitMqCheck(get_mq_settings().dsn)]
        )
    )
