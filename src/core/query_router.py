import os

from dotenv import load_dotenv
from google import genai

CONVERSATIONAL_INTENTS = {
    "greeting",
    "farewell",
    "capability_inquiry",
    "gratitude",
    "clarification",
    "small_talk",
    "affirmation",
}


class QueryRouter:
    """
    Classifies user queries into CONVERSATIONAL or RETRIEVAL intents.
    Uses a lightweight LLM call with structured output to decide routing.
    """

    def __init__(self, model: str, temperature: float):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        self.temperature = temperature

    def classify(self, query: str) -> str:
        """
        Returns "CONVERSATIONAL" or "RETRIEVAL".
        """
        prompt = f"""You are a query intent classifier for a RAG (Retrieval-Augmented Generation) chatbot.

        Your job: Decide if the user's query needs searching through documents, or can be answered conversationally.
        
        Classify as CONVERSATIONAL if the query is:
        - A greeting or farewell (e.g. "Hello", "Hi", "Bye", "Good morning")
        - A question about the assistant's capabilities (e.g. "What can you do?", "How do you work?")
        - Small talk or general chitchat (e.g. "How are you?", "That's interesting")
        - An expression of gratitude (e.g. "Thanks", "Thank you")
        - A single-word or very short acknowledgement (e.g. "Ok", "Got it", "Sure")
        
        Classify as RETRIEVAL if the query is:
        - A factual question about specific documents, topics, products, or data
        - A request to summarize, explain, or compare information from documents
        - Any question that would require looking up stored knowledge to answer correctly
        
        Respond with ONLY one word: CONVERSATIONAL or RETRIEVAL. Nothing else.
        
        User query: "{query}"
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": self.temperature, "max_output_tokens": 100},
        )

        label = response.text.strip().upper()

        # Fallback to RETRIEVAL if LLM hallucinates a non-standard label
        return label if label in ("CONVERSATIONAL", "RETRIEVAL") else "RETRIEVAL"
