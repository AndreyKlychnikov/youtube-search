import re

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from retry import retry
from urllib3.exceptions import MaxRetryError
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

from app.services.youtube.entities import Subtitle, Video


def get_channel_id(link: str) -> str:
    match = re.search(r"youtube\.com/channel/([\w-]+)", link)
    if match:
        channel_id = match.group(1)
        return channel_id

    match = re.search(r"youtube\.com/@([\w-]+)", link)
    if not match:
        raise ValueError

    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    meta = soup.find("meta", itemprop="identifier")
    if not meta:
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
    count = 0
    next_page_token = None
    while count < max_count:
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
        videos_response = (
            youtube.videos()
            .list(
                part="snippet",
                id=[
                    video["snippet"]["resourceId"]["videoId"]
                    for video in playlist_items_response["items"]
                ],
                maxResults=50,
            )
            .execute()
        )
        for video in videos_response["items"]:
            video = Video(
                id=video["id"],
                channel_id=channel_id,
                title=video["snippet"]["title"],
                published_at=video["snippet"]["publishedAt"],
                category_id=video["snippet"]["categoryId"],
            )
            videos.append(video)
        yield from videos
        count += len(videos)
        videos = []
        next_page_token = playlist_items_response.get("nextPageToken")
        if not next_page_token:
            break

    yield from videos


@retry((ConnectionError, MaxRetryError), delay=15, backoff=60, tries=3)
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
    except (
        TranscriptsDisabled,
        NoTranscriptFound,
        requests.exceptions.ConnectionError,
    ):
        return []


def get_link_to_video(video_id: str, time_code: float):
    return f"https://youtu.be/{video_id}?t={time_code}"
