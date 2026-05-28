from dataclasses import dataclass
from typing import Optional

@dataclass
class DocumentMetadata:
    source: str
    document_type: str
    page: Optional[int] = None
    section: Optional[str] = None

@dataclass
class Document:
    page_content: str
    metadata: DocumentMetadata
    