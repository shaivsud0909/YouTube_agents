from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_document(self, text: str) -> list[str]:
        return self.splitter.split_text(text)