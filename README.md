# YouTube Search

YouTube Search is a web application that allows users to search for videos on YouTube and view their subtitles. The application uses the YouTube API to search for videos and the YouTube Transcript API to retrieve the subtitles.

## Getting Started

### Prerequisites

- Python 3.10
- Poetry
- Docker (optional)

### Installation

1. Clone the repository
2. Install dependencies using poetry:
   ```
   poetry install
   ```
3. Set environment variables (see Configuration section)
4. Run the application using Uvicorn:
   ```
   uvicorn app.main:app --port 8000
   ```
   or using Docker:
   ```
   docker build -t youtube-search .
   docker run -p 8000:80 youtube-search
   ```

### Configuration

The following environment variables need to be set:

- `YOUTUBE_API_KEY`: YouTube API key
- `ELASTICSEARCH_HOST`: Elasticsearch host URL
- `ELASTICSEARCH_PORT`: Elasticsearch port

## Usage

The application provides a REST API with the following endpoints:

### GET /videos

Search for videos on YouTube.

Parameters:

- `q`: Search query (required)
- `lang`: Language code of the subtitles (default: 'en')

Response:

- `video_id`: ID of the video
- `channel_id`: ID of the channel that uploaded the video
- `text`: Subtitle text
- `start_time`: Start time of the subtitle in seconds
- `duration`: Duration of the subtitle in seconds
- `url`: URL to the video with the given start time

### POST /channels/index

Index a YouTube channel.

Request body:

```
{
    "channel_urls": ["https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw"]
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
