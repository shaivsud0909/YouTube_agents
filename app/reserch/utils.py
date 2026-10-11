import http

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


import httpx    
import trafilatura

from core.logs import logger


def extract_content(result: dict) -> str:
    """
    Extract the main article text from a DDGS search result.

    Falls back to the search snippet if the webpage cannot
    be fetched or its content cannot be extracted.
    """
    url = result.get("href")
    snippet = result.get("body", "")

    if not url:
        logger.warning("Search result does not contain a URL")
        return snippet

    try:
        response = httpx.get(
            url,
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )
        response.raise_for_status()

        content = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=True,
        )

        if content and len(content.strip()) > 200:
            logger.info("Article content extracted: %s", url)
            return content.strip()

        logger.warning("Full article extraction failed: %s", url)
        return snippet

    except http.HTTPError as exc:
        logger.warning("Failed to fetch article %s: %s", url, exc)
        return snippet

    except Exception:
        logger.exception("Unexpected content extraction error: %s", url)
        return snippet  