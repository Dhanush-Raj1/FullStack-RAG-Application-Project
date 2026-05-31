from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.core.embedding import GeminiEmbeddingGenerator
from src.core.generator import Generator
from src.core.reranker import CohereReranker
from src.core.retriever import Retriever
from src.core.vector_store import VectorStore
from src.utils.config import EMBEDDING_MODEL, LLM_MODEL, RERANKER_MODEL, TOP_K, TOP_N

app = FastAPI(title="RAG Application")

# Global instances initialized ONCE when server starts
embedding_generator = GeminiEmbeddingGenerator(model_name=EMBEDDING_MODEL)
vector_store = VectorStore()
reranker = CohereReranker(model_name=RERANKER_MODEL, top_n=TOP_N)
retriever = Retriever(
    embedder=embedding_generator,
    vector_store=vector_store,
    top_k=TOP_K,
    reranker=reranker,
)
generator = Generator(model_name=LLM_MODEL)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # 1. Retrieve & Rerank (Retriever class handles the query embedding natively inside)
        retrieved_docs = retriever.retrieve(query=request.question)

        # 2. Generate final answer
        answer = generator.generate_answer(
            question=request.question, retrieved_chunks=retrieved_docs
        )

        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
