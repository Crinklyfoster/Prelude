# RAG Evaluation Framework

This directory contains a simple, extensible evaluation framework for the Prelude.

## Dataset Structure
Add your evaluation questions to `questions.json`. The structure is simple:

```json
[
  {
    "question": "What is the objective of this document?",
    "expected_answer_contains": [
      "objective",
      "goal"
    ],
    "expected_documents": [
      "sample.pdf"
    ]
  }
]
```

## How to run

Run the evaluation runner directly from your terminal. Ensure you execute this command from the `backend` folder:

```bash
python -m tests.evaluation.run_evaluation
```

## Future Extensions

The dataset format is designed to be framework-agnostic. Later on, you can plug in more advanced evaluation tools like:
- RAGAS
- DeepEval
- TruLens

...without needing to change your dataset format.
