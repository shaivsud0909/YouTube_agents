import chromadb

from app.rag.embedings import EmbeddingService
from core.logs import logger


class ChromaVectorStore:

    def __init__(self, db_path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="research_chunks",
            metadata={"hnsw:space": "cosine"},
        )

        self.embedding_service = EmbeddingService()

    def store_chunks(self, chunks: list[dict]) -> int:
        batch_size = 100
        stored_count = 0

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            texts = [chunk["text"] for chunk in batch]
            ids = [chunk["id"] for chunk in batch]
            metadatas = [chunk["metadata"] for chunk in batch]

            embeddings = self.embedding_service.embed_documents(texts)

            self.collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            stored_count += len(batch)

        logger.info("Stored %d chunks in ChromaDB", stored_count)

        return stored_count