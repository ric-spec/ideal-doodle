from app.scrapers.base import BaseScraper, ScraperResult

API_BASE = "https://d2uvnmoyz8g0ye.cloudfront.net/api"


class ContaPublicaScraper(BaseScraper):
    portal_id = "22-conta-publica"
    portal_name = "Conta Pública"
    base_url = "https://contapublica.com.br"

    async def get_saldo(self) -> dict:
        async with self.get_client() as client:
            response = await client.get(f"{API_BASE}/saldo")
            response.raise_for_status()
            return response.json()

    async def get_extrato(self, limit: int = 100, offset: int = 0) -> dict:
        async with self.get_client() as client:
            response = await client.get(
                f"{API_BASE}/extrato",
                params={"limit": limit, "offset": offset, "order": "desc"},
            )
            response.raise_for_status()
            return response.json()

    async def get_all_extrato(self) -> list[dict]:
        all_items: list[dict] = []
        offset = 0
        limit = 100

        while True:
            data = await self.get_extrato(limit=limit, offset=offset)
            items = data.get("itens", [])
            all_items.extend(items)
            total = data.get("totalCount", 0)
            if offset + limit >= total or not items:
                break
            offset += limit

        return all_items

    async def get_registro(self) -> dict:
        async with self.get_client() as client:
            response = await client.get(f"{API_BASE}/registro")
            response.raise_for_status()
            return response.json()

    async def scrape(self) -> ScraperResult:
        result = ScraperResult(
            portal_id=self.portal_id,
            portal_name=self.portal_name,
            url=self.base_url,
        )

        try:
            saldo = await self.get_saldo()
            result.data["saldo"] = saldo
        except Exception as exc:
            result.errors.append(f"saldo: {exc}")
            result.data["saldo"] = {}

        try:
            extrato = await self.get_all_extrato()
            result.data["extrato"] = extrato
        except Exception as exc:
            result.errors.append(f"extrato: {exc}")
            result.data["extrato"] = []

        try:
            registro = await self.get_registro()
            result.data["registro"] = registro
        except Exception as exc:
            result.errors.append(f"registro: {exc}")
            result.data["registro"] = {}

        return result
