from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from src.core.embedding import GeminiEmbeddingGenerator
from src.core.llama_generator import Generator
from src.core.chunker import Chunker
from src.core.reranker import CohereReranker
from src.core.retriever import Retriever
from src.core.vector_store import VectorStore
from src.core.query_router import QueryRouter
from src.models.document import ChunkOut, QueryRequest, QueryResponse
from src.utils.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    TOP_K,
    TOP_N,
    ROUTER_MODEL,
    ROUTER_TEMPERATURE,
    FINAL_MODEL,
    CHAT_TEMPERATURE,
    RETRIEVE_TEMPERATURE,
)
from session_pipeline import SessionPipelineManager, SESSION_INDEX_REGISTRY

app = FastAPI(title="RAG Application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-frontend-b75n.onrender.com",
    ],  # Vite's default local port and deployed frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global instances initialized ONCE when server starts
chunker = Chunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
embedding_generator = GeminiEmbeddingGenerator(model=EMBEDDING_MODEL)
vector_store = VectorStore()
reranker = CohereReranker(model=RERANKER_MODEL, top_n=TOP_N)
retriever = Retriever(
    embedder=embedding_generator,
    vector_store=vector_store,
    top_k=TOP_K,
    reranker=reranker,
)
router = QueryRouter(model=ROUTER_MODEL, temperature=ROUTER_TEMPERATURE)
generator = Generator(model=FINAL_MODEL, chat_temperature=CHAT_TEMPERATURE, retrieve_temperature=RETRIEVE_TEMPERATURE)
session_manager = SessionPipelineManager(
    embedding_generator=embedding_generator, chunker=chunker
)


@app.post("/api/chat/global", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """Queries the pg vector_store and generates answer"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        intend = router.classify(request.question)

        if intend == "CONVERSATIONAL":
            answer = generator.chat(request.question)
            return QueryResponse(answer=answer, chunks=[])    # no chunks to return for conversational queries

        # Only reaches here for RETRIEVAL intents
        retrieved_docs = retriever.retrieve(query=request.question)

        answer = generator.generate_answer(
            question=request.question, retrieved_chunks=retrieved_docs
        )

        chunk_out = [
            ChunkOut(content=doc.text, source=doc.source, score=doc.score)
            for doc in retrieved_docs
        ]

        return QueryResponse(answer=answer, chunks=chunk_out)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    x_session_id: str = Header(
        ..., description="Session ID to register documents under"
    ),
):
    """Endpoint to upload documents"""
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 files allowed.")

    results = []
    for file in files:
        contents = await file.read()
        result = session_manager.process_and_register_upload(
            file_bytes=contents, filename=file.filename, session_id=x_session_id
        )
        results.append(result)

    return {"uploaded": results, "session_id": x_session_id}


@app.post("/api/chat/session", response_model=QueryResponse)
async def chat_session_documents(
    request: QueryRequest,
    x_session_id: str = Header(
        ..., description="Session identifier to map the search index"
    ),
):
    """
    QUeries the session in-memory FAISS index and generates answer
    """
    # Throw error early if index map was never initialized by a valid upload call
    if x_session_id not in SESSION_INDEX_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail="No active document workspace found for this session ID.",
        )

    try:
        intend = router.classify(request.question)

        if intend == "CONVERSATIONAL": 
            answer = generator.chat(request.question)
            return QueryResponse(answer=answer, chunks=[])  # no chunks to return for conversational queries

        retrieved_chunks = session_manager.query_session_store(
            question=request.question, session_id=x_session_id
        )

        answer = generator.generate_answer(
            question=request.question, retrieved_chunks=retrieved_chunks
        )

        # map the properties to the 'ChunkOut' model to send to the frontend UI
        output_chunks = [
            ChunkOut(content=chunk.text, source=chunk.source, score=chunk.score)
            for chunk in retrieved_chunks
        ]
        return QueryResponse(answer=answer, chunks=output_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
