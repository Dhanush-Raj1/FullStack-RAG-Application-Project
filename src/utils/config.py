from src.utils.path import ROOT_DIR

PDF_DIRECTORY = ROOT_DIR / "documents/pdfs"
MD_DIRECTORY = ROOT_DIR / "documents/markdown"
TXT_DIRECTORY = ROOT_DIR / "documents/text"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "gemini-embedding-001"   # gemini-embedding-2
EMBEDDING_DIMENSION = 3072

TOP_K = 10

TOP_N = 5
RERANKER_MODEL = "rerank-v3.5"  # rerank-v4.0-pro,   rerank-v4.0-fast,   rerank-english-v3.0

LLM_MODEL = "llama-3.3-70b-versatile"                        # "gemini-3.5-flash"        # "gemini-2.0-flash"      
