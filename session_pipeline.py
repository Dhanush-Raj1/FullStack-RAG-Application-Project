import uuid
import tempfile
import faiss
import numpy as np
import pymupdf4llm
from pathlib import Path
from typing import Dict, List, Tuple

from src.models.document import Document, DocumentMetadata, DocumentRetrievalResult
from src.core.chunker import Chunker
from src.core.embedding import GeminiEmbeddingGenerator

# Format: { session_id: (faiss_index, list_of_chunk_documents) }
SESSION_INDEX_REGISTRY: Dict[str, Tuple[faiss.Index, List[Document]]] = {}

class SessionPipelineManager:
    def __init__(self, embedding_generator: GeminiEmbeddingGenerator):
        self.embedding_generator = embedding_generator
        self.chunker = Chunker(chunk_size=500, chunk_overlap=100)

    def process_and_register_upload(self, file_bytes: bytes, filename: str, session_id: str = "default_session") -> dict:
        """
        Directly loads files from a byte stream into standard Documents, 
        chunks them, generates embeddings, and maps them to an in-memory FAISS index.
        """
        file_extension = Path(filename).suffix.lower()
        documents: List[Document] = []


        if file_extension == ".pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(file_bytes)
                temp_pdf_path = temp_pdf.name    # a safe temp path (e.g., 'C:/Temp/xyz.pdf')

            try: 
                pages_data = pymupdf4llm.to_markdown(temp_pdf_path, page_chunks=True)
                for page in pages_data:
                    text = page.get("text", "")
                    if not text.strip():
                        continue
                    
                    metadata = DocumentMetadata(
                        source=filename,
                        file_type="pdf",
                        page=page.get("metadata", {}).get("page_number"),
                    )
                    documents.append(Document(page_content=text, metadata=metadata))
            finally:
                try: 
                    Path(temp_pdf_path).unlink()   # clean up the temp file
                except Exception as e: 
                    print(f"Warning: Failed to delete temporary file '{temp_pdf_path}'. Error: {e}")

        elif file_extension == ".md":
            # Decode raw content string straight out of bytes
            raw_content = file_bytes.decode("utf-8")
            metadata = DocumentMetadata(
                source=filename,
                file_type="md",
                page=None
            )
            documents.append(Document(page_content=raw_content, metadata=metadata))

        elif file_extension == ".txt":
            # Decode raw plain text string straight out of bytes
            raw_content = file_bytes.decode("utf-8")
            metadata = DocumentMetadata(
                source=filename,
                file_type="txt",
                page=None,
                section=None
            )
            documents.append(Document(page_content=raw_content, metadata=metadata))
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        if not documents:
            raise ValueError("The uploaded file contains no extractable text content.")

       
        chunked_docs = self.chunker.chunk_documents(documents)

        if not chunked_docs:
            raise ValueError("No text chunks could be generated from the uploaded file(s).")

        raw_embeddings = []
        for chunk in chunked_docs:
            vector = self.embedding_generator.embed_text(chunk.page_content)
            raw_embeddings.append(vector)
            
        embeddings_matrix = np.atleast_2d(raw_embeddings).astype('float32')

        # In-memory FAISS index 
        dimension = embeddings_matrix.shape[1]
        faiss_index = faiss.IndexFlatL2(dimension)
        faiss_index.add(embeddings_matrix)

        # Map to our dynamic runtime session state tracking
        SESSION_INDEX_REGISTRY[session_id] = (faiss_index, chunked_docs)

    
        print("\n" + "="*50)
        print(f"🔍 [FAISS REGISTRATION DEBUG] Session ID: '{session_id}'")
        print(f"📄 File Registered: {filename} ({file_extension})")
        print(f"📐 Embeddings Matrix Shape: {embeddings_matrix.shape} -> ({embeddings_matrix.shape[0]} Chunks, {embeddings_matrix.shape[1]} Dimensions)")
        print(f"⚡ FAISS Index Total Vectors: {faiss_index.ntotal}")
        print("-"*50)
        
        print("📝 CHUNKS STORED IN REGISTRY (Mapping confirmation):")
        for idx, doc in enumerate(chunked_docs):
            # Truncate text context for cleaner log presentation
            snippet = doc.page_content.replace('\n', ' ')[:75] + "..." if len(doc.page_content) > 75 else doc.page_content
            page_info = f" | Page: {doc.metadata.page}" if doc.metadata.page else ""
            print(f"  [FAISS Vector Index #{idx}] -> {snippet}{page_info}")
        print("="*50 + "\n")

        return {
            "status": "registered",
            "filename": filename,
            "chunks_count": len(chunked_docs),
            "session_id": session_id
        }

    def query_session_store(self, question: str, session_id: str = "default_session", k: int = 3) -> List[DocumentRetrievalResult]:
        """
        Queries the in-memory FAISS vector index and returns standardized DocumentRetrievalResult records.
        """
        if session_id not in SESSION_INDEX_REGISTRY:
            return []

        # pulls the FAISS index and its corresponding chunked documents from the session registry
        faiss_index, chunked_docs = SESSION_INDEX_REGISTRY[session_id]
        
        query_vector = np.array([self.embedding_generator.embed_query(question)]).astype('float32')
        
        # Search index
        top_k = min(k, len(chunked_docs))
        distances, indices = faiss_index.search(query_vector, top_k)

        results: List[DocumentRetrievalResult] = []
        for rank, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            
            matched_chunk = chunked_docs[idx]
            score = float(1 / (1 + distances[0][rank]))  # Normalized L2 distance score

            results.append(
                DocumentRetrievalResult(
                    id=matched_chunk.metadata.chunk_id or str(uuid.uuid4()),
                    text=matched_chunk.page_content,
                    score=score,
                    source=matched_chunk.metadata.source,
                    file_type=matched_chunk.metadata.file_type,
                    page=matched_chunk.metadata.page,
                    section=matched_chunk.metadata.section,
                    chunk_index=matched_chunk.metadata.chunk_index,
                    parent_document_id=matched_chunk.metadata.parent_document_id
                )
            )
        
        return results

    def clear_session(self, session_id: str = "default_session"):
        if session_id in SESSION_INDEX_REGISTRY:
            del SESSION_INDEX_REGISTRY[session_id]