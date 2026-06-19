import chromadb


class ChromaVectorStore:
    def __init__(self, path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_chunks(self, document_id, session_id, embedded_chunks):
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in embedded_chunks:

            ids.append(f"{document_id}_{chunk['chunk_id']}")

            documents.append(chunk["text"])

            embeddings.append(chunk["embedding"])

            metadatas.append(
                {
                    "document_id": str(document_id),
                    "session_id": str(session_id),
                    "chunk_id": chunk["chunk_id"],
                }
            )

        self.collection.add(

            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )


    def search(self, query_embedding, top_k=5, session_id=None):
        if session_id:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"session_id": str(session_id)},
            )

        return self.collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )



    def delete_document(self, document_id):
        self.collection.delete(where={"document_id": str(document_id)})
