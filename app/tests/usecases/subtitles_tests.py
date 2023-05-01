from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from asynctest import MagicMock, patch, CoroutineMock

from app.usecases.subtitles import index_channels


@pytest.mark.asyncio
async def test_index_channels():
    channel_urls = ["https://www.youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow"]
    video_entity = MagicMock(
        id="test_video_id", channel_id="test_channel_id", title="test_video_title"
    )
    subtitle_entity = MagicMock(
        video_id="test_video_id", start=0, duration=10, text="test_subtitle_text"
    )
    subtitle_entity.video_id = "test_video_id"
    subtitle_entity.start = 0
    subtitle_entity.duration = 10
    subtitle_entity.text = "test_subtitle_text"

    save_videos_mock = CoroutineMock()
    save_subtitles_mock = CoroutineMock()

    with patch(
        "app.usecases.subtitles.get_channel_ids",
        return_value=["UCSJ4gkVC6NrvII8umztf0Ow"],
    ), patch(
        "app.usecases.subtitles.get_channel_videos", return_value=[video_entity]
    ), patch(
        "app.usecases.subtitles.get_video_subtitles", side_effect=[[subtitle_entity]]
    ):
        await index_channels(channel_urls, save_videos_mock, save_subtitles_mock)

    # Assert that the mocked functions were called with the expected input parameters
    save_videos_mock.assert_called_once_with([video_entity])
    save_subtitles_mock.assert_called_once_with([subtitle_entity])
