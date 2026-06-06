import os
from typing import List, Dict

from dotenv import load_dotenv
from groq import Groq

from src.models.document import DocumentRetrievalResult
from src.core.memory import ConversationMemory


class Generator:
    def __init__(
        self,
        model: str,
        chat_temperature: float,
        retrieve_temperature: float,
    ):
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found inside environmental configuration."
            )

        # Initialize the official Groq client wrapper
        self.client = Groq(api_key=api_key)
        self.model = model
        self.chat_temperature = chat_temperature
        self.retrieve_temperature = retrieve_temperature

    def build_context(self, retrieved_chunks: List[DocumentRetrievalResult]) -> str:
        context_parts = []

        for idx, chunk in enumerate(retrieved_chunks, start=1):
            context_parts.append(
                f"""
                [Chunk {idx}]
                Source: {chunk.source}
                Page: {chunk.page}
                Section: {chunk.section}

                {chunk.text}
            """.strip()
            )

        return "\n\n".join(context_parts)

    def chat(self, query: str, history: List[Dict] = []) -> str:
        """
        Handles conversational queries that don't need document retrieval.
        """
        prompt = """
        You are a helpful RAG assistant with two core capabilities:
        1. Answer questions from a built-in knowledge base of tech specs, space mission records, and architecture docs.
        2. Accept user-uploaded documents (PDF, Markdown, TXT) and answer questions from them.


        For greetings, small talk, or questions about your capabilities — respond naturally and concisely.
        When asked what you can do, explain that users can ask questions about the documents 
        in the knowledge base or from the uploaded documents and you'll find and summarize relevant information.        
        """

        messages = [{"role": "system", "content": prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.chat_temperature,
        )
        return response.choices[0].message.content

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[DocumentRetrievalResult],
        history: List[Dict] = [],
    ) -> str:
        context = self.build_context(retrieved_chunks)

        prompt = """
            You are a helpful assistant answering questions using retrieved document context.

            Instructions:
            - Answer only using the provided context.
            - If the answer is not contained in the context, say:
              "I could not find the answer in the provided documents."
            - Be concise and accurate.
        """
        user_message = f"""
        Context: 
            {context}

        Question:
            {question}
        """


        messages = [{"role": "system", "content": prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.retrieve_temperature,
        )

        # Pull out the message text safely
        return response.choices[0].message.content
