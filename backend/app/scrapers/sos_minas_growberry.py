from .base import BaseScraper, ScraperResult


class SosMinasGrowberryScraper(BaseScraper):
    portal_id = "05-sos-minas-growberry"
    portal_name = "SOS Minas (Growberry)"
    base_url = "https://sosminas.growberry.com.br"

    async def get_pedidos(self, cidade: str | None = None) -> list[dict]:
        async with self.get_client() as client:
            response = await client.get(f"{self.base_url}/api/pedidos.php")
            response.raise_for_status()
            pedidos: list[dict] = response.json()

        if cidade:
            pedidos = [p for p in pedidos if p.get("cidade", "").lower() == cidade.lower()]

        return pedidos

    async def get_pedido(self, pedido_id: int) -> dict | None:
        async with self.get_client() as client:
            response = await client.get(f"{self.base_url}/api/pedidos.php", params={"id": pedido_id})
            response.raise_for_status()
            data = response.json()

        if not data:
            return None

        if isinstance(data, list):
            return data[0] if data else None

        return data

    async def get_voluntarios(
        self,
        page: int = 1,
        cidade: str | None = None,
        categoria: str | None = None,
    ) -> dict:
        params: dict[str, str | int] = {"page": page}
        if cidade:
            params["cidade"] = cidade
        if categoria:
            params["categoria"] = categoria

        async with self.get_client() as client:
            response = await client.get(f"{self.base_url}/api/voluntarios.php", params=params)
            response.raise_for_status()
            return response.json()

    async def get_all_voluntarios(self, cidade: str | None = None) -> list[dict]:
        all_voluntarios: list[dict] = []
        page = 1

        while True:
            result = await self.get_voluntarios(page=page, cidade=cidade)
            data = result.get("data", [])
            all_voluntarios.extend(data)

            if not result.get("hasMore", False):
                break

            page += 1

        return all_voluntarios

    async def get_doacoes(self, cidade: str | None = None) -> list[dict]:
        params: dict[str, str | int] = {"tipo": "doacao", "page": 1}
        if cidade:
            params["cidade"] = cidade

        all_doacoes: list[dict] = []
        page = 1

        while True:
            params["page"] = page
            async with self.get_client() as client:
                response = await client.get(f"{self.base_url}/api/voluntarios.php", params=params)
                response.raise_for_status()
                result = response.json()

            data = result.get("data", [])
            all_doacoes.extend(data)

            if not result.get("hasMore", False):
                break

            page += 1

        return all_doacoes

    async def get_comentarios(self, pedido_id: int) -> list[dict]:
        async with self.get_client() as client:
            response = await client.get(
                f"{self.base_url}/api/comentarios.php",
                params={"id_pedido": pedido_id},
            )
            response.raise_for_status()
            data = response.json()

        if isinstance(data, list):
            return data

        return []

    async def get_logistica(self) -> dict:
        async with self.get_client() as client:
            response = await client.get(f"{self.base_url}/api/logistica.php")
            response.raise_for_status()
            return response.json()

    async def scrape(self) -> ScraperResult:
        result = ScraperResult(
            portal_id=self.portal_id,
            portal_name=self.portal_name,
            url=self.base_url,
        )

        try:
            pedidos = await self.get_pedidos()
        except Exception as exc:
            pedidos = []
            result.errors.append(f"get_pedidos: {exc}")

        try:
            all_voluntarios = await self.get_all_voluntarios()
            voluntarios = [v for v in all_voluntarios if v.get("tipo") != "doacao"]
            doacoes = [v for v in all_voluntarios if v.get("tipo") == "doacao"]
        except Exception as exc:
            voluntarios = []
            doacoes = []
            result.errors.append(f"get_all_voluntarios: {exc}")

        result.data = {
            "pedidos": pedidos,
            "voluntarios": voluntarios,
            "doacoes": doacoes,
        }

        return result
