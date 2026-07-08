import chromadb
from chromadb.api.types import Documents, Embeddings, IDs, Metadatas


class ChromaVectorStore:
    def __init__(self, path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_chunks(
        self,
        document_id,
        current_user_id,
        embedded_chunks,
    ):

        ids: IDs = []
        documents: Documents = []
        embeddings: Embeddings = []
        metadatas: Metadatas = []

        for chunk in embedded_chunks:
            ids.append(f"{document_id}_{chunk['chunk_id']}")

            documents.append(chunk["text"])

            embeddings.append(chunk["embedding"])

            metadatas.append(
                {
                    "document_id": str(document_id),
                    "user_id": str(current_user_id),
                    "chunk_id": str(
                        chunk["chunk_id"]
                    ),  # Chroma stub requires str
                }
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding,
        current_user_id,
        top_k=5,
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"user_id": str(current_user_id)},
        )

    def get_chunk(
        self,
        document_id: str,
        chunk_id: int,
    ):
        result = self.collection.get(
            where={
                "$and": [
                    {"document_id": {"$eq": document_id}},
                    {"chunk_id": {"$eq": chunk_id}},
                ]
            },
            include=[
                "documents",
                "metadatas",
            ],
        )

        if not result["ids"]:
            return None

        assert result["documents"] is not None
        assert result["metadatas"] is not None
        return {
            "text": result["documents"][0],
            "metadata": result["metadatas"][0],
        }

    def delete_document(self, document_id):
        self.collection.delete(where={"document_id": str(document_id)})
