# YouTube Search

YouTube Search is a web application that allows users to search for videos on YouTube and view their subtitles. The application uses the YouTube API to search for videos and the YouTube Transcript API to retrieve the subtitles.

## Getting Started

### Prerequisites

- Python 3.10
- Poetry
- Docker (optional)

### Installation
Specify env variables in `compose.env` file.

For running app in docker use:
```shell
make compose
```

For running app in development mode use:
```shell
make run-local-services
make run-local-app  # Run backend
make run-local-celery  # Run celery
```
In this case database is running in a container and app is running locally.


### Configuration

The following environment variables need to be set:

- `YOUTUBE_API_KEY`: YouTube API key
- `ELASTICSEARCH_HOST`: Elasticsearch host URL
- `ELASTICSEARCH_PORT`: Elasticsearch port

## Makefile

Makefile has four targets:

- `install`: Installs project dependencies using Poetry.
- `compose`: Starts Docker Compose in detached mode.
- `run-local-services`: Starts services in docker container (Postgres, Redis, Elasticsearch, Kibana), applies database
migrations and creates elasticsearch indices. It also copies the `compose.env` file to `.env` for environment variable
configuration.
- `run-local-app`: Starts FastApi application
- `run-local-celery`: Starts Celery application
- `migrate`: Runs Alembic migration to upgrade the database to the latest revision.


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

## CI/CD: Github Actions
This GitHub Action template automates the build and deployment of a Docker
image to a remote server using Ansible.

### Inputs
For proper work of actions you need to specify following secrets for a
repository. How to specify secrets: [Github docs](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository)

#### `DOCKERHUB_USERNAME`

The username for authenticating with the Docker registry.

#### `DOCKERHUB_TOKEN`

The password or token for authenticating with the Docker registry.

#### `SSH_HOST`

The hostname or IP address of the remote server to deploy the Docker image to.

#### `SSH_PRIVATE_KEY`

The SSH private key used to authenticate with the remote server.

#### `YOUTUBE_API_KEY`

The API key used to interact with Youtube API

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
