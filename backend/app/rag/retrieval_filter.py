from typing import cast

from chromadb.api.types import Where


class RetrievalFilter:

    @staticmethod
    def build(
        user_id: str,
        document_ids: list[str] | None = None,
    ) -> Where:

        user_filter: Where = cast(Where, {
            "user_id": {
                "$eq": user_id,
            }
        })
        filters: list[Where] = [user_filter]

        if document_ids:
            doc_filter: Where = cast(Where, {
                "document_id": {
                    "$in": document_ids
                }
            })
            filters.append(doc_filter)

        if len(filters) == 1:
            return filters[0]

        return cast(Where, {
            "$and": filters
        })
