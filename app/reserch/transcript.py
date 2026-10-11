from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.reserch.base_reserch import BaseResearch
from app.reserch.schema import ResearchRequest, ResearchResult
from app.reserch.utils import extract_transcript
from core.config import settings
from core.logs import logger


class TranscriptResearch(BaseResearch):
    """Research a topic using YouTube video discovery."""

    def __init__(self):
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=settings.youtube_api_key,
        )

    def research(self, request: ResearchRequest) -> ResearchResult:
        topic = request.topic
        date = request.date
        max_results = request.max_results
        language = request.language

        try:
            # Build the search query.
            query = f"{topic}".strip()

            published_after = (
                    date.astimezone(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                )

            response = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order="relevance",
                publishedAfter=published_after,
                relevanceLanguage=language,
            ).execute()

            logger.info("YouTube search response: %s", response)

            sources = []

            for item in response.get("items", []):
                video_id = item.get("id", {}).get("videoId")

                if not video_id:
                    continue

                snippet = item.get("snippet", {})

                sources.append({
                    "source_type": "youtube",
                    "title": snippet.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "content": extract_transcript(video_id),
                    "published_at": snippet.get("publishedAt"),
                    "metadata": {
                        "channel_title": snippet.get("channelTitle", ""),
                        "description": snippet.get("description", "")
                    },
                })

            return ResearchResult(
                topic=topic,
                sources=sources,
                errors=[],
            )

        except HttpError as exc:
            return ResearchResult(
                topic=topic,
                sources=[],
                errors=[f"YouTube API error: {exc}"],
            )

        except Exception as exc:
            logger.error(f"Unexpected error during YouTube research: {exc}")
            return ResearchResult(
                topic=topic,
                sources=[],
                errors=[f"Unexpected error: {exc}"],
            )

# transcript_research_service = TranscriptResearch()
# print(transcript_research_service.research(ResearchRequest(topic="claude", max_results=5, date=datetime.now(timezone.utc), language="en")))