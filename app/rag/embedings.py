import ollama


class EmbeddingService:

    def __init__(self, model: str = "qwen3-embedding:0.6b"):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = ollama.embed(
            model=self.model,
            input=texts,
        )

        return response["embeddings"]