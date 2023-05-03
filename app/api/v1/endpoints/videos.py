from fastapi import APIRouter

from app.schemas.search_result import SearchResult
from app.usecases.search import search as search_usecase

router = APIRouter()


@router.get("/")
async def search(q: str, lang: str = "en") -> list[SearchResult]:
    return await search_usecase(q, lang)
