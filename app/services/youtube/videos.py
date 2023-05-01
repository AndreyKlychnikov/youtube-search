import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

from app.services.youtube.entities import Subtitle, Video


def get_channel_id(link: str) -> str:
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    meta = soup.find("meta", itemprop="channelId")
    if not meta:
        raise ValueError
    return meta["content"]


def get_channel_videos(
    channel_id: str, api_key: str, max_count: int = 500
) -> list[Video]:
    """
    Retrieves a list of videos from a YouTube channel specified by channel ID.
    :param channel_id: The channel ID to retrieve videos from.
    :param api_key: The YouTube API key.
    :param max_count: Maximum count of videos per channel
    :returns: A list of video objects, where each object contains information about a
    video, including its ID, title, description, and thumbnail URL.
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    channel_response = (
        youtube.channels().list(part="contentDetails", id=channel_id).execute()
    )
    playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"][
        "uploads"
    ]

    videos = []
    next_page_token = None
    while len(videos) < max_count:
        playlist_items_response = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            .execute()
        )
        for item in playlist_items_response["items"]:
            video = Video(
                id=item["snippet"]["resourceId"]["videoId"],
                channel_id=channel_id,
                title=item["snippet"]["title"],
            )
            videos.append(video)
        next_page_token = playlist_items_response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


def get_video_subtitles(video_id: str, lang: str = "en") -> list[Subtitle]:
    """
    Retrieves the subtitles for a YouTube video.

    :param video_id: The ID of the YouTube video.
    :param lang: The language of the subtitles. Defaults to 'en'.

    :returns: The subtitles for the video, as a single string.
    """
    try:
        captions = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return [
            Subtitle(**caption, language=lang, video_id=video_id)
            for caption in captions
        ]
    except (TranscriptsDisabled, NoTranscriptFound):
        return []