from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel


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


@dataclass
class DocumentRetrievalResult:
    id: str
    text: str
    score: float

    source: str
    file_type: str

    page: Optional[int]
    section: Optional[str]

    chunk_index: Optional[int]
    parent_document_id: Optional[str]


class QueryRequest(BaseModel):
    question: str
    source: Optional[str] = None
    score: Optional[float] = None


class ChunkOut(BaseModel):
    content: str
    source: Optional[str] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    chunks: List[ChunkOut] = []
