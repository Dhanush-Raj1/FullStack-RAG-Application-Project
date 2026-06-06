import os
import re
from typing import Dict, List

from dotenv import load_dotenv
from groq import Groq

from src.models.document import DocumentRetrievalResult


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

        You also have access to the current conversation history. Use it to answer 
        - If the user asks a personal or contextual question ("what is my name?", 
          "what did I say earlier?", "do you remember me?"), look back through the 
          conversation history and answer directly from it.
        - Never say "I don't have memory" or "I can't remember" — the conversation 
          history is always available to you.

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
            You are a helpful assistant answering questions using retrieved document context 
            and the conversation history provided above.

            Instructions:
            - Use the conversation history to resolve references like "it", "that", "this", 
              "the previous answer", or "what I asked earlier" before answering.
            - Answer using the provided context where relevant.
            - If the answer is not in the context but can be resolved from conversation 
              history, answer from history.
            - If neither context nor history contains the answer, say:
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

    def rewrite_query(self, question: str, history: List[Dict]) -> str:
        """
        Rewrites a vague or coreference query into a self-contained search query
        using conversation history.
        """
        if not history:
            return question  # nothing to resolve against, use as-is

        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in history[-5:]  # last 3 turns
        )

        prompt = f"""
        Given this conversation history:
            {history_text}

            Rewrite this question into a clear, self-contained search query 
            that replaces all vague references ("it", "that", "this", "the previous") 
            with their actual subjects from the history.

            If the question is already self-contained, return it unchanged.
            Return ONLY the rewritten query. Nothing else.

            Question: {question}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()

    COREFERENCE_TRIGGERS = re.compile(
        r"\b(it|its|this|that|these|those|they|them|their|"
        r"the (previous|last|above|earlier)|what (you|i) (said|mentioned|asked)|"
        r"tell me more|explain (that|this|it)|elaborate|go on|continue|"
        r"what does (it|that|this) mean|how (does|did) (it|that|this))\b",
        re.IGNORECASE,
    )
    
    def needs_rewrite(self, question: str, history: List[Dict]) -> bool:
        """Fast check — only rewrite if coreference signals are present."""
        if not history:
            return False
        
        return bool(self.COREFERENCE_TRIGGERS.search(question))
