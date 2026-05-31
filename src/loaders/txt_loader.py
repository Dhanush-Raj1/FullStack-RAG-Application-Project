from pathlib import Path
from typing import List

from src.models.document import Document, DocumentMetadata


def load_texts(directory_path: Path) -> List[Document]:
    """
    Load all plain text files from a directory and establish metadata foundations.
    """
    directory_path = Path(directory_path)

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    text_files = sorted(directory_path.glob("*.txt"))
    documents: List[Document] = []

    for txt_file in text_files:
        content = txt_file.read_text(encoding="utf-8")

        metadata = DocumentMetadata(
            source=txt_file.name, file_type="txt", page=None, section=None
        )

        documents.append(Document(page_content=content, metadata=metadata))

    return documents
