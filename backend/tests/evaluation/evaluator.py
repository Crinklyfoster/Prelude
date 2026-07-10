from app.services.rag_service import RAGService
from tests.evaluation.metrics import EvaluationMetrics


class RAGEvaluator:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        self.metrics = EvaluationMetrics()

    def evaluate(self, dataset: list[dict]):
        self.metrics.total_questions = len(dataset)

        for item in dataset:
            result = self.rag_service.answer_question(question=item["question"])

            # Check Answer
            expected_contains = item.get("expected_answer_contains", [])
            answer_text = result.get("answer", "")
            if expected_contains:
                answer_ok = all(
                    word.lower() in answer_text.lower()
                    for word in expected_contains
                )
            else:
                answer_ok = True

            if answer_ok:
                self.metrics.answer_accuracy += 1

            # Check Retrieval
            expected_docs = item.get("expected_documents", [])
            docs = {
                s.get("document_id")
                for s in result.get("sources", [])
            }
            if expected_docs:
                retrieval_ok = any(
                    d in docs
                    for d in expected_docs
                )
            else:
                retrieval_ok = True

            if retrieval_ok:
                self.metrics.retrieval_accuracy += 1

        return self.metrics
