import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.workers.scraper_worker import run_all_scrapers

logger = logging.getLogger(__name__)


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        run_all_scrapers,
        trigger="interval",
        hours=settings.SCRAPER_INTERVAL_HOURS,
        id="scraper_all_portals",
        replace_existing=True,
    )
    logger.info("Cron configurado: interval=%dh", settings.SCRAPER_INTERVAL_HOURS)
    return scheduler
