import ollama


class OllamaEmbedder:

    def __init__(
        self,
        model_name: str = "nomic-embed-text"
    ):
        self.model_name = model_name

    def generate_embedding(
        self,
        text: str
    ):
        response = ollama.embeddings(
            model=self.model_name,
            prompt=text
        )

        return response["embedding"]

    def generate_embeddings(
        self,
        chunks: list
    ):
        embeddings = []

        for chunk in chunks:
            vector = self.generate_embedding(
                chunk["text"]
            )

            embeddings.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "embedding": vector
                }
            )

        return embeddings