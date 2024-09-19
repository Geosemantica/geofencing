from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.schedulers.outbox import publish_outbox
from app.schedulers.settings import get_task_settings


def get_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    config = get_task_settings()
    if config.outbox_publish_enabled:
        scheduler.add_job(publish_outbox,
                          'interval',
                          seconds=config.outbox_scan_interval,
                          args=(config.outbox_batch_size,))

    return scheduler
