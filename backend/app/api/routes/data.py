from typing import Any

from fastapi import APIRouter, Query
from sqlmodel import col, func, select

from app.api.deps import SessionDep
from app.models import FeedItem, Outro, Pedido, Pet, PontoAjuda, Voluntario

router = APIRouter(tags=["data"])


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _list_response(data: list[Any], count: int) -> dict[str, Any]:
    return {"data": data, "count": count}


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

@router.get("/pedidos")
async def list_pedidos(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    portal_id: str | None = None,
    cidade: str | None = None,
    categoria: str | None = None,
    status: str | None = None,
) -> Any:
    q = select(Pedido)
    if portal_id:
        q = q.where(Pedido.portal_id == portal_id)
    if cidade:
        q = q.where(Pedido.cidade.ilike(f"%{cidade}%"))  # type: ignore[union-attr]
    if categoria:
        q = q.where(Pedido.categoria.ilike(f"%{categoria}%"))  # type: ignore[union-attr]
    if status:
        q = q.where(Pedido.status == status)

    count = (await session.exec(select(func.count()).select_from(q.subquery()))).one()
    items = (await session.exec(q.order_by(col(Pedido.scraped_at).desc()).offset(skip).limit(limit))).all()
    return _list_response(items, count)


# ---------------------------------------------------------------------------
# Voluntários
# ---------------------------------------------------------------------------

@router.get("/voluntarios")
async def list_voluntarios(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    portal_id: str | None = None,
    cidade: str | None = None,
    categoria: str | None = None,
) -> Any:
    q = select(Voluntario)
    if portal_id:
        q = q.where(Voluntario.portal_id == portal_id)
    if cidade:
        q = q.where(Voluntario.cidade.ilike(f"%{cidade}%"))  # type: ignore[union-attr]
    if categoria:
        q = q.where(Voluntario.categoria.ilike(f"%{categoria}%"))  # type: ignore[union-attr]

    count = (await session.exec(select(func.count()).select_from(q.subquery()))).one()
    items = (await session.exec(q.order_by(col(Voluntario.scraped_at).desc()).offset(skip).limit(limit))).all()
    return _list_response(items, count)


# ---------------------------------------------------------------------------
# Pontos de Ajuda
# ---------------------------------------------------------------------------

@router.get("/pontos")
async def list_pontos(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    portal_id: str | None = None,
    cidade: str | None = None,
    tipo: str | None = None,
) -> Any:
    q = select(PontoAjuda)
    if portal_id:
        q = q.where(PontoAjuda.portal_id == portal_id)
    if cidade:
        q = q.where(PontoAjuda.cidade.ilike(f"%{cidade}%"))  # type: ignore[union-attr]
    if tipo:
        q = q.where(PontoAjuda.tipo == tipo)

    count = (await session.exec(select(func.count()).select_from(q.subquery()))).one()
    items = (await session.exec(q.order_by(col(PontoAjuda.scraped_at).desc()).offset(skip).limit(limit))).all()
    return _list_response(items, count)


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

@router.get("/pets")
async def list_pets(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    portal_id: str | None = None,
    cidade: str | None = None,
    tipo: str | None = None,
    especie: str | None = None,
) -> Any:
    q = select(Pet)
    if portal_id:
        q = q.where(Pet.portal_id == portal_id)
    if cidade:
        q = q.where(Pet.cidade.ilike(f"%{cidade}%"))  # type: ignore[union-attr]
    if tipo:
        q = q.where(Pet.tipo == tipo)
    if especie:
        q = q.where(Pet.especie.ilike(f"%{especie}%"))  # type: ignore[union-attr]

    count = (await session.exec(select(func.count()).select_from(q.subquery()))).one()
    items = (await session.exec(q.order_by(col(Pet.scraped_at).desc()).offset(skip).limit(limit))).all()
    return _list_response(items, count)


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------

@router.get("/feed")
async def list_feed(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    portal_id: str | None = None,
    tipo: str | None = None,
    urgente: bool | None = None,
) -> Any:
    q = select(FeedItem)
    if portal_id:
        q = q.where(FeedItem.portal_id == portal_id)
    if tipo:
        q = q.where(FeedItem.tipo == tipo)
    if urgente is not None:
        q = q.where(FeedItem.urgente == urgente)

    count = (await session.exec(select(func.count()).select_from(q.subquery()))).one()
    items = (await session.exec(q.order_by(col(FeedItem.scraped_at).desc()).offset(skip).limit(limit))).all()
    return _list_response(items, count)


# ---------------------------------------------------------------------------
# Outros
# ---------------------------------------------------------------------------

@router.get("/outros")
async def list_outros(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    portal_id: str | None = None,
    tipo: str | None = None,
) -> Any:
    q = select(Outro)
    if portal_id:
        q = q.where(Outro.portal_id == portal_id)
    if tipo:
        q = q.where(Outro.tipo == tipo)

    count = (await session.exec(select(func.count()).select_from(q.subquery()))).one()
    items = (await session.exec(q.order_by(col(Outro.scraped_at).desc()).offset(skip).limit(limit))).all()
    return _list_response(items, count)
