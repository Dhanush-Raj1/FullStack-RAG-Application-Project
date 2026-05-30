from src.utils.path import ROOT_DIR

PDF_DIRECTORY = ROOT_DIR / "documents/pdfs"

CHUNK_SIZE = 500
OVERLAP_SIZE = 100

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 3072

RETRIEVE_TOP_K = 10

RERANK_TOP_N = 5
COHERE_RERANK_MODEL = "rerank-v3.5"  # rerank-v4.0-pro,   rerank-v4.0-fast,   rerank-english-v3.0


LLM_MODEL = "gemini-2.0-flash"
