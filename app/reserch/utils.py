from youtube_transcript_api import YouTubeTranscriptApi
from core.logs import logger


def extract_transcript(video_id: str) -> str:
    """Extract the available transcript for a YouTube video."""

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        text = " ".join(
            snippet.text for snippet in transcript
        )

        logger.info("Transcript extracted for video: %s", video_id)

        return text

    except Exception as e:
        return ""