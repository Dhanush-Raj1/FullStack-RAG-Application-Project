from typing import List, Optional, Dict, Any

from src.models.document import DocumentRetrievalResult
from src.core.embedding import GeminiEmbeddingGenerator
from src.core.vector_store import VectorStore
from src.core.reranker import CohereReranker


class Retriever:
    def __init__(
        self,
        embedder: GeminiEmbeddingGenerator,
        vector_store: VectorStore,
        top_k: int,
        reranker: Optional[CohereReranker] = None,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker
        self.top_k = top_k

    def retrieve(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[DocumentRetrievalResult]:

        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)

        # vector search + metadaa filtering
        rows = self.vector_store.similarity_search(
            query_embedding=query_embedding, k=self.top_k, filters=filters
        )

        results = []
        for row in rows:
            (
                chunk_id,
                text_content,
                distance,
                source,
                file_type,
                page,
                section,
                chunk_index,
                parent_document_id,
            ) = row

            results.append(
                DocumentRetrievalResult(
                    id=chunk_id,
                    text=text_content,
                    score=1 - float(distance),
                    source=source,
                    file_type=file_type,
                    page=page,
                    section=section,
                    chunk_index=chunk_index,
                    parent_document_id=parent_document_id,
                )
            )

        # Reranking with cohere
        if self.reranker and results:
            return self.reranker.rerank(query=query, documents=results)

        # fall back if reranker not configured
        return results
