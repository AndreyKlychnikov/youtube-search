import pytest

from app.services.youtube.entities import Subtitle, Video
from app.services.youtube.videos import get_channel_id, get_video_subtitles, get_channel_videos


def test_get_channel_id_valid_link():
    link = 'https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw'
    channel_id = get_channel_id(link)
    assert channel_id == 'UC_x5XG1OV2P6uZZ5FSM9Ttw'


def test_get_channel_id_valid_link_with_username():
    link = 'https://www.youtube.com/@kurzgesagt'
    channel_id = get_channel_id(link)
    assert channel_id == 'UCsXVk37bltHxD1rDPwtNM8Q'


def test_get_channel_id_invalid_link():
    link = 'https://www.youtube.com/invalid-channel-link'
    with pytest.raises(ValueError):
        get_channel_id(link)


def test_get_channel_id_missing_meta_tag():
    link = 'https://www.youtube.com/'
    with pytest.raises(ValueError):
        get_channel_id(link)


def test_get_channel_videos(api_key):
    channel_id = "UCI1p0_8jEGM9yabxPib5WzQ"
    videos = get_channel_videos(channel_id, api_key)
    for video in videos:
        assert isinstance(video, Video)
        assert video.id
        assert video.channel_id
        assert video.title


def test_get_video_subtitles_valid():
    video_id = 'MTJK-4Eu4r8'
    lang = 'en'
    subtitles = get_video_subtitles(video_id, lang)
    assert isinstance(subtitles, list)
    for subtitle in subtitles:
        assert isinstance(subtitle, Subtitle)
        assert subtitle.video_id == video_id
        assert subtitle.language == lang


def test_get_videos_subtitles_invalid():
    video_id = 'INVALID_VIDEO_ID'
    lang = 'en'
    subtitles = get_video_subtitles(video_id, lang)
    assert isinstance(subtitles, list)
    assert len(subtitles) == 0
