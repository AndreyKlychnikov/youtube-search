from fastapi import APIRouter

from app.schemas.search_result import SearchResult
from app.services.elastic.subtitles import search_within_subtitles

router = APIRouter()


@router.get("/")
async def search(q: str, lang: str = "en") -> list[SearchResult]:
    results = await search_within_subtitles(q, lang)
    return [SearchResult(**result) for result in results]


