from app.reserch.base_reserch import BaseResearch
from app.reserch.schema import ResearchRequest, ResearchResult
from ddgs import DDGS
from core.logs import logger

class ScrapingResearch(BaseResearch):
    """Research a topic using web scraping."""

    def research(self, request: ResearchRequest) -> ResearchResult:
        try:
            topic = request.topic
            region = request.region
            language = request.language
            max_results = request.max_results

            with DDGS() as search:
                query = f"{topic}"
                results = search.text(query, max_results=max_results, region=region, language=language)

                sources = []
                for rank, result in enumerate(results, start=1):
                    logger.info(
                        "Search result: %s - %s",
                        result.get("title"),
                        result.get("href"),
                    )

                    source = {
                        "source_type": "web",
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "content": result.get("body", ""),
                        "published_at": published_at if (published_at := result.get("date")) else None,
                        "metadata": {
                            "rank": rank,
                        },
                    }

                    sources.append(source)

                return ResearchResult(
                    topic=topic,
                    sources=sources,
                    errors=[],
                )
    
        except Exception as e:
            logger.error(f"Error during web scraping research: {e}")
            return ResearchResult(
                topic=request.topic,
                sources=sources if 'sources' in locals() else [],
                errors=[str(e)],
            )

research_service = ScrapingResearch()

request = ResearchRequest(topic="indian stock market", max_results=5, region="IN", language="en")
print(research_service.research(request))