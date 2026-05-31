import logging

from src.core.chunker import Chunker
from src.core.embedding import GeminiEmbeddingGenerator
from src.core.vector_store import VectorStore
from src.loaders.md_loader import load_markdowns
from src.loaders.pdf_loader import load_pdfs
from src.loaders.txt_loader import load_texts
from src.preprocess.md_cleaner import MarkdownCleaner
from src.preprocess.pdf_cleaner import PDFCleaner
from src.preprocess.txt_cleaner import TextCleaner
from src.utils.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    MD_DIRECTORY,
    PDF_DIRECTORY,
    TXT_DIRECTORY,
)

logging.basicConfig(level=logging.INFO)


def run_ingestion():
    # Initialize Components
    logging.info("Initializing components...")
    pdf_cleaner, md_cleaner, text_cleaner = (
        PDFCleaner(),
        MarkdownCleaner(),
        TextCleaner(),
    )
    chunker = Chunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    embedding_generator = GeminiEmbeddingGenerator(model_name=EMBEDDING_MODEL)
    vector_store = VectorStore()

    # Extract and Clean
    logging.info("Loading documents...")
    cleaned_docs = [
        *pdf_cleaner.clean_documents(load_pdfs(PDF_DIRECTORY)),
        *md_cleaner.clean_documents(load_markdowns(MD_DIRECTORY)),
        *text_cleaner.clean_documents(load_texts(TXT_DIRECTORY)),
    ]
    logging.info(f"Loaded and cleaned {len(cleaned_docs)} documents across all formats.")

    # Chunk
    logging.info(f"Processing and embedding {len(cleaned_docs)} documents...")
    final_chunks = chunker.chunk_documents(cleaned_docs)
    logging.info(f"Chunked documents into {len(final_chunks)} chunks.")

    # embed
    embedded_docs = embedding_generator.embed_documents(final_chunks)
    logging.info(f"Generated embeddings for {len(embedded_docs)} chunks.")

    logging.info("Initializing vector store and adding documents...")
    vector_store.add_documents(embedded_docs)
    logging.info(f"Ingestion complete! Added {vector_store.get_total_count()} documents.")


if __name__ == "__main__":
    run_ingestion()
