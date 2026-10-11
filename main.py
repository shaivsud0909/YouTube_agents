import json
from pathlib import Path

from datetime import datetime, timedelta, timezone

from app.rag.ingestion import ResearchIngestion
from app.rag.ingestion import ResearchIngestion
from app.reserch.schema import ResearchRequest
from app.reserch.scrap import ScrapingResearch
from app.reserch.transcript import TranscriptResearch
from core.logs import logger


OUTPUT_DIR = Path("data/research")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    topic = "Dhruv rathee detained in delhi"

    request = ResearchRequest(
        topic=topic,
        date=datetime.now(timezone.utc)- timedelta(days=1),
        region="IN",
        language="en",
        max_results=10,
    )

    all_sources = []
    errors = []

    # Step 1: Web research
    try:
        logger.info("Starting web research")

        web_result = ScrapingResearch().research(request)

        all_sources.extend(web_result.sources)
        errors.extend(web_result.errors)

    except Exception as exc:
        logger.exception("Web research failed")
        errors.append(f"Web research failed: {exc}")

    # Step 2: YouTube research
    try:
        logger.info("Starting YouTube research")

        youtube_result = TranscriptResearch().research(request)
        logger.info("YouTube research completed with %d sources and %d errors", len(youtube_result.sources), len(youtube_result.errors))    
        all_sources.extend(youtube_result.sources)
        errors.extend(youtube_result.errors)

    except Exception as exc:
        logger.exception("YouTube research failed")
        errors.append(f"YouTube research failed: {exc}")

    # Step 3: Prepare JSON output
    result = {
        "topic": topic,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_sources": len(all_sources),
        "sources": [
            source.model_dump(mode="json")
            for source in all_sources
        ],
        "errors": errors,
    }

    # Step 4: Save results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"research_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    logger.info("Research pipeline completed")
    logger.info("Total sources collected: %s", len(all_sources))
    logger.info("Results saved to %s", output_file)

    logger.info("Rag pipeline started")

    ingestion = ResearchIngestion()
    ingestion.ingest(output_file)

    logger.info("Rag pipeline completed")

if __name__ == "__main__":
    main()