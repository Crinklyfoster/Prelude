import json
import re
from collections import defaultdict
from pathlib import Path


class LexicalIndex:
    STORAGE_DIR = Path("storage/lexical")

    INDEX_FILE = STORAGE_DIR / "inverted_index.json"
    LENGTH_FILE = STORAGE_DIR / "chunk_lengths.json"
    METADATA_FILE = STORAGE_DIR / "metadata.json"
    STATS_FILE = STORAGE_DIR / "stats.json"

    def __init__(self):
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        self.inverted_index = defaultdict(dict)
        self.chunk_lengths = {}
        self.chunk_metadata = {}
        self.document_frequency = {}
        self.total_chunks = 0

        self.load()

    def tokenize(self, text: str):
        return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    def add_document(
        self,
        document_id,
        current_user_id,
        chunks,
    ):

        for chunk in chunks:
            chunk_id = f"{document_id}_{chunk['chunk_id']}"

            tokens = self.tokenize(chunk["text"])

            self.chunk_lengths[chunk_id] = len(tokens)

            self.chunk_metadata[chunk_id] = {
                "document_id": str(document_id),
                "chunk_id": chunk["chunk_id"],
                "user_id": str(current_user_id),
            }

            token_counts = defaultdict(int)

            for token in tokens:
                token_counts[token] += 1

            for token, freq in token_counts.items():
                self.inverted_index[token][chunk_id] = freq

            self.total_chunks += 1

        self._update_document_frequency()

        self.save()

    def remove_document(self, document_id):

        document_id = str(document_id)

        chunks_to_remove = [
            chunk_id
            for chunk_id, metadata in self.chunk_metadata.items()
            if metadata["document_id"] == document_id
        ]

        for chunk_id in chunks_to_remove:
            self.chunk_lengths.pop(chunk_id, None)

            self.chunk_metadata.pop(chunk_id, None)

            tokens_to_remove = []
            for token, postings in self.inverted_index.items():
                postings.pop(chunk_id, None)
                if not postings:
                    tokens_to_remove.append(token)

            for token in tokens_to_remove:
                del self.inverted_index[token]

            self.total_chunks -= 1

        self._update_document_frequency()

        self.save()

    def _update_document_frequency(self):

        self.document_frequency = {
            token: len(postings)
            for token, postings in self.inverted_index.items()
        }

    def save(self):

        with open(self.INDEX_FILE, "w") as f:
            json.dump(self.inverted_index, f)

        with open(self.LENGTH_FILE, "w") as f:
            json.dump(self.chunk_lengths, f)

        with open(self.METADATA_FILE, "w") as f:
            json.dump(self.chunk_metadata, f)

        with open(self.STATS_FILE, "w") as f:
            json.dump(
                {
                    "document_frequency": self.document_frequency,
                    "total_chunks": self.total_chunks,
                },
                f,
            )

    def load(self):

        if self.INDEX_FILE.exists():
            with open(self.INDEX_FILE) as f:
                self.inverted_index = defaultdict(
                    dict,
                    json.load(f),
                )

        if self.LENGTH_FILE.exists():
            with open(self.LENGTH_FILE) as f:
                self.chunk_lengths = json.load(f)

        if self.METADATA_FILE.exists():
            with open(self.METADATA_FILE) as f:
                self.chunk_metadata = json.load(f)

        if self.STATS_FILE.exists():
            with open(self.STATS_FILE) as f:
                stats = json.load(f)

                self.document_frequency = stats.get(
                    "document_frequency",
                    {},
                )

                self.total_chunks = stats.get(
                    "total_chunks",
                    0,
                )
