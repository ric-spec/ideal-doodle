from app.scrapers.ajude_io import AjudeIoScraper
from app.scrapers.base import BaseScraper, ScraperResult
from app.scrapers.cidade_que_cuida import CidadeQueCuidaScraper
from app.scrapers.emergencia_mg import EmergenciaMgScraper
from app.scrapers.minas_emergencia import MinasEmergenciaScraper
from app.scrapers.sos_animais_mg import SosAnimaisMgScraper
from app.scrapers.sos_minas_growberry import SosMinasGrowberryScraper
from app.scrapers.sosjf_online import SosJfOnlineScraper
from app.scrapers.sosjf_org import SosJfOrgScraper

__all__ = [
    "BaseScraper",
    "ScraperResult",
    "EmergenciaMgScraper",
    "MinasEmergenciaScraper",
    "SosAnimaisMgScraper",
    "SosMinasGrowberryScraper",
    "SosJfOrgScraper",
    "SosJfOnlineScraper",
    "AjudeIoScraper",
    "CidadeQueCuidaScraper",
]
