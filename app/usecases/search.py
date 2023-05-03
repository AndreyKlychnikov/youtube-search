from app.schemas.search_result import SearchResult
from app.services.elastic.subtitles import search_within_subtitles
from app.services.youtube.videos import get_link_to_video


async def search(q: str, lang: str = "en"):
    results = await search_within_subtitles(q, lang)
    return [
        SearchResult(
            **result,
            url=get_link_to_video(
                result["video_id"],
                max(0, int(result["start_time"]) - 3),  # make bigger fragment
            )
        )
        for result in results
    ]
