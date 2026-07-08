from app.core.config import settings

class PromptBuilder:
    def __init__(self):
        self.max_context_chars = 12000

    def build(
        self,
        chunks: list[dict],
    ) -> str:
        """
        Build the retrieval context supplied to the LLM.
        """
        chunks = sorted(
            chunks,
            key=lambda c: (
                c.get("rerank_score")
                or c.get("rrf_score")
                or 0
            ),
            reverse=True,
        )

        seen = set()
        context_parts = []
        current_size = 0

        for chunk in chunks:
            text = chunk["text"].strip()

            if text in seen:
                continue

            seen.add(text)

            formatted = (
                f"[Source]\n"
                f"Document ID: {chunk['document_id']}\n"
                f"Chunk: {chunk['chunk_id']}\n\n"
                f"{text}\n"
            )

            if (
                current_size + len(formatted)
                > self.max_context_chars
            ):
                break

            context_parts.append(formatted)
            current_size += len(formatted)

        return "\n\n".join(context_parts)
