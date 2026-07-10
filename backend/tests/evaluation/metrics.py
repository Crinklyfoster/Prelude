from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    total_questions: int = 0
    answer_accuracy: int = 0
    retrieval_accuracy: int = 0

    @property
    def answer_score(self):
        if self.total_questions == 0:
            return 0
        return self.answer_accuracy / self.total_questions

    @property
    def retrieval_score(self):
        if self.total_questions == 0:
            return 0
        return self.retrieval_accuracy / self.total_questions
