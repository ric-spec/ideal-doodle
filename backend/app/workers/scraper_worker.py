import asyncio
import logging

from app.scrapers import (
    AjudaEmjfScraper,
    AjudaImediataScraper,
    AjudaJfArcteiScraper,
    AjudeIoScraper,
    AjudeJfScraper,
    AjudeJuizDeForaScraper,
    CidadeQueCuidaScraper,
    ContaPublicaScraper,
    EmergenciaMgScraper,
    InterdicoesJfScraper,
    MiAuAjudaScraper,
    MinasEmergenciaScraper,
    OndeDoarScraper,
    ScraperResult,
    SosAnimaisMgScraper,
    SosJfOnlineScraper,
    SosJfOrgScraper,
    SosMinasGrowberryScraper,
    SosSerLuzJfScraper,
    UnidosPorJfScraper,
    ZonaDaMataAlertasScraper,
)

logger = logging.getLogger(__name__)

SCRAPERS = [
    EmergenciaMgScraper,
    MinasEmergenciaScraper,
    SosAnimaisMgScraper,
    SosMinasGrowberryScraper,
    SosJfOrgScraper,
    SosJfOnlineScraper,
    AjudeIoScraper,
    CidadeQueCuidaScraper,
    AjudeJuizDeForaScraper,
    SosSerLuzJfScraper,
    AjudaImediataScraper,
    AjudaJfArcteiScraper,
    OndeDoarScraper,
    InterdicoesJfScraper,
    AjudaEmjfScraper,
    MiAuAjudaScraper,
    ZonaDaMataAlertasScraper,
    UnidosPorJfScraper,
    AjudeJfScraper,
    ContaPublicaScraper,
]


async def _run_one(cls) -> ScraperResult:
    scraper = cls()
    try:
        result = await scraper.scrape()
        level = logging.WARNING if result.errors else logging.INFO
        logger.log(level, "[%s] done — errors=%d", scraper.portal_name, len(result.errors))
        return result
    except Exception as exc:
        logger.error("[%s] failed: %s", scraper.portal_name, exc)
        return ScraperResult(
            portal_id=scraper.portal_id,
            portal_name=scraper.portal_name,
            url=scraper.base_url,
            errors=[str(exc)],
        )


async def run_all_scrapers() -> list[ScraperResult]:
    logger.info("Scraper worker started (%d portais)", len(SCRAPERS))
    results = await asyncio.gather(*[_run_one(cls) for cls in SCRAPERS])
    ok = sum(1 for r in results if not r.errors)
    logger.info("Scraper worker done: %d/%d OK", ok, len(results))
    return list(results)
