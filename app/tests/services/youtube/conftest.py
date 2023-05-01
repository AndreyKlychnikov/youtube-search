import os

import pytest


@pytest.fixture
def api_key():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise ValueError("No API key found in environment variables.")
    return key
