import os
from typing import List

from dotenv import load_dotenv
from google import genai

from src.models.document import DocumentRetrievalResult


class Generator:
    def __init__(self, model_name: str):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        self.client = genai.Client(api_key=api_key)

        self.model_name = model_name

    def _build_context(self, retrieved_chunks: List[DocumentRetrievalResult]) -> str:

        context_parts = []

        for idx, chunk in enumerate(retrieved_chunks, start=1):
            context_parts.append(f"""
                [Chunk {idx}]
                Source: {chunk.source}
                Page: {chunk.page}
                Section: {chunk.section}

                {chunk.text}
            """.strip())

        return "\n\n".join(context_parts)

    def generate_answer(
        self, question: str, retrieved_chunks: List[DocumentRetrievalResult]
    ) -> str:

        context = self._build_context(retrieved_chunks)

        prompt = f"""
            You are a helpful assistant answering questions using retrieved document context.

            Instructions:d
            - Answer only using the provided context.
            - If the answer is not contained in the context, say:
              "I could not find the answer in the provided documents."
            - Be concise and accurate.
            - Mention the source i.e source, page, section.

            Context:
            {context}

            Question:
            {question}
        """

        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt
        )

        return response.text
