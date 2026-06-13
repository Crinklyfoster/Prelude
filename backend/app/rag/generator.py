import ollama


class Generator:

    def __init__(
        self,
        model_name: str = "qwen3:8b"
    ):
        self.model_name = model_name

    def generate(
        self,
        context: str,
        question: str
    ):
        prompt = f"""
You are a helpful assistant.

Answer the question using ONLY the provided context.

If the answer is not contained in the context, say:
"I could not find that information in the document."

Context:
{context}

Question:
{question}

Answer:
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]