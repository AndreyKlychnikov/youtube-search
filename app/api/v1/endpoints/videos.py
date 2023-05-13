from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.container import Container, get_container
from app.schemas.search_result import SearchResult

router = APIRouter()


@router.get("/")
async def search(
    q: str,
    lang: str = "en",
    youtube_category_ids: Annotated[list[str], Query()] = None,
    container: Container = Depends(get_container),
) -> list[SearchResult]:
    return await container.search_service.search(q, lang, youtube_category_ids)
