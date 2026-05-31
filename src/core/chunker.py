from pathlib import Path
from typing import List, Dict, Optional, Any

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.models.document import Document, DocumentMetadata


class Chunker:
    """
    Handles chunking strategies for multiple document types,
    preserving markdown structures and enforcing size constraints.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        headers_to_split_on: Optional[List[tuple]] = None,
    ):
        # Fallback to default markdown headers if none provided
        if headers_to_split_on is None:
            headers_to_split_on = [
                ("#", "header_1"),
                ("##", "header_2"),
                ("###", "header_3"),
            ]

        # Initialize LangChain splitters
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,  # Crucial for preserving structural layout context
        )

    def _extract_section_name(self, metadata: Dict[str, Any]) -> Optional[str]:
        """Extract the most specific available markdown header from metadata."""
        return (
            metadata.get("header_3")
            or metadata.get("header_2")
            or metadata.get("header_1")
        )

    def _generate_chunk_id(
        self, source: str, chunk_index: int, page: Optional[int] = None
    ) -> str:
        """Generate deterministic, globally unique readable chunk IDs."""
        stem = Path(source).stem.lower().replace(" ", "_")
        if page is not None:
            return f"{stem}_page_{page}_chunk_{chunk_index}"
        return f"{stem}_chunk_{chunk_index}"

    def _create_chunk_document(
        self,
        content: str,
        original_metadata: DocumentMetadata,
        chunk_index: int,
        section: Optional[str] = None,
    ) -> Document:
        """Create a chunked Document object with enriched metadata."""
        chunk_id = self._generate_chunk_id(
            source=original_metadata.source,
            page=original_metadata.page,
            chunk_index=chunk_index,
        )

        parent_document_id = (
            Path(original_metadata.source).stem.lower().replace(" ", "_")
        )

        metadata = DocumentMetadata(
            source=original_metadata.source,
            file_type=original_metadata.file_type,
            page=original_metadata.page,
            section=section,
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            parent_document_id=parent_document_id,
        )

        return Document(page_content=content, metadata=metadata)

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Main chunking dispatcher with size constraints enforced across all document routes.
        """
        all_chunks = []
        document_counters: Dict[str, int] = {}

        for document in documents:
            file_type = document.metadata.file_type.lower()
            source_file = document.metadata.source

            if source_file not in document_counters:
                document_counters[source_file] = 0

            # Structured Text (PDF and MD/Markdown)
            if file_type in ["pdf", "md", "markdown"]:
                header_splits = self.markdown_splitter.split_text(document.page_content)
                last_active_section = None

                for split in header_splits:
                    extracted_section = self._extract_section_name(split.metadata)
                    if extracted_section:
                        last_active_section = extracted_section

                    # Enforce chunk_size constraints via Recursive Character Splitting
                    recursive_chunks = self.recursive_splitter.split_text(
                        split.page_content
                    )

                    for chunk_text in recursive_chunks:
                        chunk_doc = self._create_chunk_document(
                            content=chunk_text,
                            original_metadata=document.metadata,
                            chunk_index=document_counters[source_file],
                            section=last_active_section,
                        )
                        all_chunks.append(chunk_doc)
                        document_counters[source_file] += 1

            # Plain Text (TXT)
            elif file_type == "txt":
                chunks = self.recursive_splitter.split_text(document.page_content)

                for chunk_text in chunks:
                    chunk_doc = self._create_chunk_document(
                        content=chunk_text,
                        original_metadata=document.metadata,
                        chunk_index=document_counters[source_file],
                        section=None,
                    )
                    all_chunks.append(chunk_doc)
                    document_counters[source_file] += 1

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        return all_chunks
