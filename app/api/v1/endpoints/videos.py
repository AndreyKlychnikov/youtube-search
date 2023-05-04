from fastapi import APIRouter, Depends

from app.container import Container, get_container
from app.schemas.search_result import SearchResult

router = APIRouter()


@router.get("/")
async def search(
    q: str, lang: str = "en", container: Container = Depends(get_container)
) -> list[SearchResult]:
    return await container.search_service.search(q, lang)
