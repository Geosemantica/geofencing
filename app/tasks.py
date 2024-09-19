from app.schedulers.scheduler import get_scheduler


async def run_interval_tasks():
    scheduler = get_scheduler()
    await scheduler.start()
