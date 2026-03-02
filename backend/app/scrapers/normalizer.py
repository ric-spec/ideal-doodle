"""
Normaliza ScraperResult bruto → NormalizedResult com schema unificado.

IDs seguem o padrão: portal_id:cidade:raw_id
"""
from __future__ import annotations

from typing import Any

from app.schemas.normalized import (
    FeedItem,
    NormalizedResult,
    Outro,
    Pedido,
    Pet,
    PontoAjuda,
    Voluntario,
)
from app.scrapers.base import ScraperResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _first(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Retorna o primeiro valor não-nulo/vazio entre as chaves fornecidas."""
    for k in keys:
        v = d.get(k)
        if v is not None and v != "":
            return v
    return default


def _geo(d: dict[str, Any]) -> tuple[float | None, float | None]:
    lat = _first(d, "lat", "latitude")
    lng = _first(d, "lng", "longitude", "lon")
    try:
        return (
            float(lat) if lat is not None else None,
            float(lng) if lng is not None else None,
        )
    except (TypeError, ValueError):
        return None, None


def _city_slug(d: dict[str, Any], *keys: str, fallback: str = "mg") -> str:
    v = _first(d, *keys) or fallback
    return str(v).lower().replace(" ", "_")


# ---------------------------------------------------------------------------
# dispatcher
# ---------------------------------------------------------------------------

_NORMALIZERS: dict[str, Any] = {}


def normalize(result: ScraperResult) -> NormalizedResult:
    fn = _NORMALIZERS.get(result.portal_id)
    if fn is None:
        return NormalizedResult()
    return fn(result)


def normalize_all(results: list[ScraperResult]) -> NormalizedResult:
    combined = NormalizedResult()
    for r in results:
        nr = normalize(r)
        combined.pedidos.extend(nr.pedidos)
        combined.voluntarios.extend(nr.voluntarios)
        combined.pontos.extend(nr.pontos)
        combined.pets.extend(nr.pets)
        combined.feed.extend(nr.feed)
        combined.outros.extend(nr.outros)
    return combined


# ---------------------------------------------------------------------------
# per-portal normalizers
# ---------------------------------------------------------------------------

def _emergencia_mg(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    for i, item in enumerate(r.data.get("emergency_contacts", [])):
        nr.outros.append(Outro(
            id=f"{pid}:jf:contato:{i}",
            **base,
            tipo="contato_emergencia",
            titulo=item.get("nome"),
            contato=item.get("telefone"),
            raw=item,
        ))

    for i, item in enumerate(r.data.get("help_links", [])):
        nr.outros.append(Outro(
            id=f"{pid}:jf:link:{i}",
            **base,
            tipo="link",
            titulo=item.get("titulo"),
            descricao=item.get("descricao"),
            url=item.get("url"),
            raw=item,
        ))

    for i, item in enumerate(r.data.get("animal_shelters", [])):
        lat, lng = _geo(item)
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:jf:abrigo_animal:{i}",
            **base,
            tipo="abrigo_animal",
            nome=item.get("nome"),
            contato=item.get("telefone") or item.get("whatsapp_url"),
            itens=item.get("animais", []),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for i, item in enumerate(r.data.get("transport_volunteers", [])):
        nr.voluntarios.append(Voluntario(
            id=f"{pid}:jf:transporte:{i}",
            **base,
            nome=item.get("nome"),
            categoria="transporte",
            contato=item.get("telefone") or item.get("whatsapp_url"),
            raw=item,
        ))

    return nr


_NORMALIZERS["01-emergencia-mg"] = _emergencia_mg


# ---------------------------------------------------------------------------

def _sos_animais_mg(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    tipo_map = {
        "lost": "perdido",
        "found": "encontrado",
        "adoption": "adocao",
    }
    for category, tipo in tipo_map.items():
        for item in r.data.get(category, []):
            city = _city_slug(item, "city", fallback="mg")
            raw_id = item.get("id", "")
            nr.pets.append(Pet(
                id=f"{pid}:{city}:{raw_id}",
                **base,
                tipo=tipo,
                nome=item.get("pet_name"),
                especie=item.get("animal_type"),
                descricao=item.get("description"),
                status=item.get("status"),
                contato=item.get("phone"),
                cidade=item.get("city"),
                imagem_url=item.get("image_url"),
                raw=item,
            ))

    return nr


_NORMALIZERS["sos_animais_mg"] = _sos_animais_mg


# ---------------------------------------------------------------------------

def _sos_minas_growberry(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    for item in r.data.get("pedidos", []):
        raw_id = _first(item, "id", "ID", "codigo") or ""
        city = _city_slug(item, "cidade", fallback="mg")
        lat, lng = _geo(item)
        nr.pedidos.append(Pedido(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            titulo=_first(item, "titulo", "title", "descricao"),
            descricao=_first(item, "descricao", "description", "detalhe"),
            categoria=_first(item, "categoria", "tipo"),
            status=item.get("status"),
            contato=_first(item, "telefone", "phone", "contato", "whatsapp"),
            cidade=item.get("cidade"),
            bairro=_first(item, "bairro", "neighborhood"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for item in r.data.get("voluntarios", []):
        raw_id = _first(item, "id", "ID") or ""
        city = _city_slug(item, "cidade", fallback="mg")
        lat, lng = _geo(item)
        nr.voluntarios.append(Voluntario(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            nome=_first(item, "nome", "name"),
            descricao=_first(item, "descricao", "description", "habilidades"),
            categoria=_first(item, "categoria", "tipo"),
            contato=_first(item, "telefone", "phone", "contato", "whatsapp"),
            cidade=item.get("cidade"),
            bairro=_first(item, "bairro", "neighborhood"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for i, item in enumerate(r.data.get("doacoes", [])):
        raw_id = _first(item, "id", "ID") or str(i)
        city = _city_slug(item, "cidade", fallback="mg")
        lat, lng = _geo(item)
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            tipo="doacao",
            nome=_first(item, "nome", "name", "titulo"),
            endereco=_first(item, "endereco", "address"),
            cidade=item.get("cidade"),
            bairro=_first(item, "bairro", "neighborhood"),
            contato=_first(item, "telefone", "phone", "contato"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    return nr


_NORMALIZERS["05-sos-minas-growberry"] = _sos_minas_growberry


# ---------------------------------------------------------------------------

def _sosjf_org(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    tipo_map = {
        "alerts": "alerta",
        "news": "noticia",
        "reports": "relatorio",
    }
    for category, tipo in tipo_map.items():
        for item in r.data.get(category, []):
            raw_id = item.get("id", "")
            nr.feed.append(FeedItem(
                id=f"{pid}:jf:{raw_id}",
                **base,
                tipo=tipo,
                titulo=_first(item, "titulo", "title", "name"),
                descricao=_first(item, "descricao", "description", "content", "body"),
                url=_first(item, "url", "link", "href"),
                data=str(item["date"]) if item.get("date") else None,
                urgente=bool(item.get("urgente") or item.get("urgent")),
                raw=item,
            ))

    return nr


_NORMALIZERS["sosjf_org"] = _sosjf_org


# ---------------------------------------------------------------------------

def _sosjf_online(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    tipo_map = {
        "collection_points": "coleta",
        "shelters": "abrigo",
    }
    for key, tipo in tipo_map.items():
        for i, item in enumerate(r.data.get(key, [])):
            raw_id = _first(item, "id", "ID") or str(i)
            bairro = item.get("neighborhood") or item.get("bairro")
            lat, lng = _geo(item)
            nr.pontos.append(PontoAjuda(
                id=f"{pid}:jf:{raw_id}",
                **base,
                tipo=tipo,
                nome=_first(item, "name", "nome"),
                endereco=_first(item, "address", "endereco"),
                bairro=bairro,
                cidade="Juiz de Fora",
                contato=_first(item, "phone", "telefone", "contato"),
                horario=_first(item, "horario", "hours"),
                itens=item.get("itens") or item.get("items") or [],
                lat=lat,
                lng=lng,
                raw=item,
            ))

    return nr


_NORMALIZERS["07-sosjf-online"] = _sosjf_online


# ---------------------------------------------------------------------------

def _ajude_io(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    for item in r.data.get("help_requests", []):
        raw_id = item.get("id", "")
        city = _city_slug(item, "cidade", "city", fallback="jf")
        lat, lng = _geo(item)
        nr.pedidos.append(Pedido(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            titulo=_first(item, "titulo", "title", "tipo"),
            descricao=_first(item, "descricao", "description", "detalhes"),
            categoria=_first(item, "categoria", "tipo", "category"),
            status=item.get("status"),
            nome=_first(item, "nome", "name", "solicitante"),
            contato=_first(item, "telefone", "phone", "contato", "whatsapp"),
            cidade=_first(item, "cidade", "city"),
            bairro=_first(item, "bairro", "neighborhood"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for item in r.data.get("volunteer_offers", []):
        raw_id = item.get("id", "")
        city = _city_slug(item, "cidade", "city", fallback="jf")
        lat, lng = _geo(item)
        nr.voluntarios.append(Voluntario(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            nome=_first(item, "nome", "name"),
            descricao=_first(item, "descricao", "description", "habilidades"),
            categoria=_first(item, "categoria", "tipo", "category"),
            contato=_first(item, "telefone", "phone", "contato"),
            cidade=_first(item, "cidade", "city"),
            bairro=_first(item, "bairro", "neighborhood"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for i, item in enumerate(r.data.get("donation_points", [])):
        raw_id = item.get("id") or str(i)
        city = _city_slug(item, "cidade", "city", fallback="jf")
        lat, lng = _geo(item)
        itens_raw = item.get("itens") or item.get("items") or item.get("necessidades") or []
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            tipo="doacao",
            nome=_first(item, "nome", "name"),
            endereco=_first(item, "endereco", "address"),
            cidade=_first(item, "cidade", "city"),
            bairro=_first(item, "bairro", "neighborhood"),
            contato=_first(item, "telefone", "phone", "contato"),
            horario=_first(item, "horario", "hours"),
            itens=itens_raw if isinstance(itens_raw, list) else [str(itens_raw)],
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for i, item in enumerate(r.data.get("shelters", [])):
        raw_id = item.get("id") or item.get("name") or str(i)
        lat, lng = _geo(item)
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:jf:abrigo:{raw_id}",
            **base,
            tipo="abrigo",
            nome=item.get("name") or item.get("nome"),
            bairro=item.get("neighborhood") or item.get("bairro"),
            cidade="Juiz de Fora",
            lat=lat,
            lng=lng,
            raw=item,
        ))

    return nr


_NORMALIZERS["08-ajude-io"] = _ajude_io


# ---------------------------------------------------------------------------

def _cidade_que_cuida(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    def _users(item: dict[str, Any]) -> dict[str, Any]:
        u = item.get("users")
        return u if isinstance(u, dict) else {}

    for item in r.data.get("pedidos", []):
        raw_id = item.get("id", "")
        u = _users(item)
        lat, lng = _geo(item)
        nr.pedidos.append(Pedido(
            id=f"{pid}:jf:{raw_id}",
            **base,
            titulo=_first(item, "titulo", "title"),
            descricao=_first(item, "descricao", "description"),
            categoria=_first(item, "categoria", "tipo"),
            status=item.get("status"),
            nome=u.get("nome"),
            contato=u.get("telefone") or _first(item, "telefone", "phone"),
            cidade="Juiz de Fora",
            bairro=_first(item, "bairro") or u.get("bairro"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for item in r.data.get("voluntarios", []):
        raw_id = item.get("id", "")
        u = _users(item)
        lat, lng = _geo(item)
        nr.voluntarios.append(Voluntario(
            id=f"{pid}:jf:{raw_id}",
            **base,
            nome=_first(item, "titulo", "title") or u.get("nome"),
            descricao=_first(item, "descricao", "description"),
            categoria=_first(item, "categoria", "tipo"),
            contato=u.get("telefone") or _first(item, "telefone"),
            cidade="Juiz de Fora",
            bairro=_first(item, "bairro") or u.get("bairro"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for item in r.data.get("doacoes", []):
        raw_id = item.get("id", "")
        u = _users(item)
        lat, lng = _geo(item)
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:jf:{raw_id}",
            **base,
            tipo="doacao",
            nome=_first(item, "titulo", "title"),
            descricao=_first(item, "descricao", "description"),
            cidade="Juiz de Fora",
            bairro=_first(item, "bairro") or u.get("bairro"),
            contato=u.get("telefone") or _first(item, "telefone"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    for item in r.data.get("entidades", []):
        raw_id = item.get("id", "")
        lat, lng = _geo(item)
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:jf:entidade:{raw_id}",
            **base,
            tipo="entidade",
            nome=_first(item, "nome", "name", "titulo"),
            endereco=_first(item, "endereco", "address"),
            cidade="Juiz de Fora",
            bairro=_first(item, "bairro", "neighborhood"),
            contato=_first(item, "telefone", "phone", "contato"),
            horario=_first(item, "horario", "horarios"),
            lat=lat,
            lng=lng,
            raw=item,
        ))

    return nr


_NORMALIZERS["09"] = _cidade_que_cuida


# ---------------------------------------------------------------------------

def _minas_emergencia(r: ScraperResult) -> NormalizedResult:
    nr = NormalizedResult()
    pid, pname, purl, sa = r.portal_id, r.portal_name, r.url, r.scraped_at
    base = dict(portal_id=pid, portal_name=pname, portal_url=purl, scraped_at=sa)

    for i, item in enumerate(r.data.get("pontos", [])):
        raw_id = _first(item, "id", "ID") or str(i)
        city = _city_slug(item, "cidade", fallback="mg")
        lat, lng = _geo(item)
        itens_raw = item.get("itens") or []
        nr.pontos.append(PontoAjuda(
            id=f"{pid}:{city}:{raw_id}",
            **base,
            tipo=item.get("tipo") or "ponto",
            nome=item.get("nome"),
            endereco=item.get("endereco"),
            cidade=item.get("cidade"),
            bairro=item.get("bairro"),
            contato=item.get("contato"),
            horario=item.get("horario"),
            itens=itens_raw if isinstance(itens_raw, list) else [],
            lat=lat,
            lng=lng,
            raw=item,
        ))

    return nr


_NORMALIZERS["minas_emergencia"] = _minas_emergencia
