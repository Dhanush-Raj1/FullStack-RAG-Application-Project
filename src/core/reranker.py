import os
from typing import List

import cohere
from dotenv import load_dotenv

from src.models.document import DocumentRetrievalResult


class CohereReranker:
    def __init__(self, model_name: str, top_n: int = 5):
        load_dotenv()
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY not found in environment variables.")

        # Initialize the Cohere Client
        self.client = cohere.ClientV2(api_key=api_key)
        self.model_name = model_name
        self.top_n = top_n

    def rerank(
        self, query: str, documents: List[DocumentRetrievalResult]
    ) -> List[DocumentRetrievalResult]:
        """
        Reranks a list of candidate DocumentRetrievalResults using Cohere's Cross-Encoder API.
        """
        if not documents:
            return []

        # Ensure we don't request a top_n larger than our candidate list size
        top_n = min(self.top_n, len(documents))

        texts_to_rerank = [doc.text for doc in documents]

        response = self.client.rerank(
            model=self.model_name, query=query, documents=texts_to_rerank, top_n=top_n
        )

        reranked_results = []

        # Map Cohere's response objects back to your structured RetrievalResults
        for result in response.results:
            original_index = result.index
            original_doc = documents[original_index]

            # Update the score with Cohere's precise relevance score
            original_doc.score = float(result.relevance_score)
            reranked_results.append(original_doc)

        return reranked_results
