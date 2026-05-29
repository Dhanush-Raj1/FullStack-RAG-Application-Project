from dataclasses import dataclass
from typing import Optional

@dataclass
class DocumentMetadata:
    source: str
    file_type: str
    page: Optional[int] = None
    section: Optional[str] = None

    chunk_id: Optional[str] = None
    chunk_index: Optional[int] = None

    parent_document_id: Optional[str] = None


@dataclass
class Document:
    page_content: str
    metadata: DocumentMetadata
    