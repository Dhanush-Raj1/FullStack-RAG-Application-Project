from pathlib import Path
from typing import List

import pymupdf4llm

from src.models.document import Document, DocumentMetadata


def load_pdfs(pdf_directory: Path) -> List[Document]:
    """
    Load all PDFs from a directory.
    """

    pdf_directory = Path(pdf_directory)

    if not pdf_directory.exists():
        raise FileNotFoundError(f"Directory not found: {pdf_directory}")

    pdf_files = sorted(pdf_directory.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_directory}")

    documents: List[Document] = []

    for pdf_path in pdf_files:
        pages_data = pymupdf4llm.to_markdown(str(pdf_path), page_chunks=True)

        for page in pages_data:
            text = page["text"]

            if not text.strip():
                continue

            metadata = DocumentMetadata(
                source=pdf_path.name,
                file_type="pdf",
                page=page["metadata"]["page_number"],
            )

            documents.append(Document(page_content=text, metadata=metadata))

    return documents
