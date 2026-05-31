from pathlib import Path
from typing import List

from src.models.document import Document, DocumentMetadata


def load_markdowns(directory_path: Path) -> List[Document]:
    """
    Load all markdown files from a directory.
    """

    directory_path = Path(directory_path)

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    markdown_files = sorted(directory_path.glob("*.md"))

    documents: List[Document] = []

    for md_file in markdown_files:
        content = md_file.read_text(encoding="utf-8")

        metadata = DocumentMetadata(
            source=md_file.name,
            file_type="md",
            page=None,
        )

        documents.append(Document(page_content=content, metadata=metadata))

    return documents
