
import chromadb

from app.rag.embedings import EmbeddingService
from core.logs import logger


class ResearchRetriever:

    def __init__(self, db_path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="research_chunks",
            metadata={"hnsw:space": "cosine"},
        )

        self.embedding_service = EmbeddingService()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        # 1. Convert the research question into an embedding
        query_embedding = self.embedding_service.embed_documents(
            [query]
        )[0]

        # 2. Search ChromaDB for similar chunks
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        # 3. Format the retrieved evidence
        retrieved_documents = []

        for index, text in enumerate(results["documents"][0]):
            retrieved_documents.append({
                "text": text,
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            })

        logger.info(
            "Retrieved %d chunks for query: %s",
            len(retrieved_documents),
            query,
        )

        return retrieved_documents



if __name__ == "__main__":
    retriever = ResearchRetriever()
    query = "What time was dhruv rathee detained in delhi?"
    top_k = 5

    try:
        results = retriever.retrieve(query=query, top_k=top_k)
        for idx, result in enumerate(results, start=1):
            print(f"Result {idx}:")
            print(f"Text: {result['text']}")
            print(f"Metadata: {result['metadata']}")
            print(f"Distance: {result['distance']}\n")
    except ValueError as ve:
        logger.error("ValueError: %s", ve)
    except Exception as e:
        logger.error("An error occurred during retrieval: %s", e)