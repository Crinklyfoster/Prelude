import hashlib
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=settings.CHUNK_SEPARATORS,
        )

    def _normalize(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def chunk_text(self, text: str):

        text = self._normalize(text)

        chunks = self.splitter.split_text(text)

        seen = set()

        output = []

        for idx, chunk in enumerate(chunks):
            if len(chunk) < settings.MIN_CHUNK_LENGTH:
                continue

            digest = hashlib.sha256(
                chunk.encode("utf-8")
            ).hexdigest()

            if settings.ENABLE_CHUNK_DEDUP:
                if digest in seen:
                    continue
                seen.add(digest)

            output.append(
                {
                    "chunk_id": idx,
                    "text": chunk,
                    "hash": digest,
                    "length": len(chunk),
                }
            )

        return output
