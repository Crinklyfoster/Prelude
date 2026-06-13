import chromadb


class ChromaVectorStore:

    def __init__(
        self,
        path: str = "./chroma_db"
    ):
        self.client = chromadb.PersistentClient(
            path=path
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="documents"
            )
        )

    def add_chunks(
        self,
        document_id,
        embedded_chunks
    ):
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in embedded_chunks:

            ids.append(
                f"{document_id}_{chunk['chunk_id']}"
            )

            documents.append(
                chunk["text"]
            )

            embeddings.append(
                chunk["embedding"]
            )

            metadatas.append(
                {
                    "document_id": str(document_id),
                    "chunk_id": chunk["chunk_id"]
                }
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )