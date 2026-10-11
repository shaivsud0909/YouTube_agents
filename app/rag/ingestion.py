import json
from pathlib import Path

from core.logs import logger
from app.rag.chunking import TextChunker
from app.rag.vectordb import ChromaVectorStore


class ResearchIngestion:

    def __init__(self):
        self.chunker = TextChunker()
        self.vector_db = ChromaVectorStore()

    def ingest(self, json_file_path: Path) -> int:
        try:
            # 1. Load research JSON
            with json_file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            documents = []

            for index, source in enumerate(data.get("sources", [])):
                content = source.get("content", "").strip()

                if not content:
                    logger.warning(
                        "Skipping source with empty content: %s",
                        source.get("title", "Unknown title"),
                    )
                    continue

                documents.append({
                    "id": f"source_{index}",
                    "text": content,
                    "metadata": {
                        "topic": data.get("topic", ""),
                        "title": source.get("title", ""),
                        "url": source.get("url", ""),
                        "source_type": source.get("source_type", "unknown"),
                    },
                })

            logger.info("Topic: %s", data.get("topic"))
            logger.info("Documents prepared: %d", len(documents))

            # 2. Chunk documents
            chunks = []

            for document in documents:
                text_chunks = self.chunker.chunk_document(
                    document["text"]
                )

                for chunk_index, chunk_text in enumerate(text_chunks):
                    chunks.append({
                        "id": f'{document["id"]}_chunk_{chunk_index}',
                        "text": chunk_text,
                        "metadata": {
                            **document["metadata"],
                            "parent_document_id": document["id"],
                            "chunk_index": chunk_index,
                        },
                    })

            logger.info("Total chunks created: %d", len(chunks))

            if not chunks:
                logger.warning("No chunks available for vector storage")
                return 0

            # 3. Generate embeddings and store in ChromaDB
            stored_count = self.vector_db.store_chunks(chunks)

            logger.info(
                "Research ingestion completed. Chunks stored: %d",
                stored_count,
            )

            return stored_count

        except (OSError, json.JSONDecodeError):
            logger.exception(
                "Failed to read research JSON: %s",
                json_file_path,
            )
            raise
