import json
import os
import sys

# Add backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.rag_service import RAGService
from tests.evaluation.evaluator import RAGEvaluator


def main():
    current_dir = os.path.dirname(__file__)
    questions_file = os.path.join(current_dir, "questions.json")

    with open(questions_file, "r") as f:
        dataset = json.load(f)

    rag = RAGService()
    evaluator = RAGEvaluator(rag)

    print(f"Running evaluation on {len(dataset)} questions...")
    metrics = evaluator.evaluate(dataset)

    print("\n======================")
    print(f"Questions : {metrics.total_questions}")
    print(f"Answer Accuracy : {metrics.answer_score * 100:.1f}%")
    print(f"Retrieval Accuracy : {metrics.retrieval_score * 100:.1f}%")
    print("======================")


if __name__ == "__main__":
    main()
