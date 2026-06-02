import re
from typing import List

from src.models.document import Document


class TextCleaner:
    def __init__(self):

        self.CITATION_PATTERN = re.compile(r"\[\d+\]")

        self.EM_DASH_PATTERN = re.compile(r"[\u2014\u2015]")
        self.HAIR_SPACE_PATTERN = re.compile(r"[\u200a\u200b]")

        # Target multiple periods/ellipses used in text transcriptions
        self.ELLIPSIS_PATTERN = re.compile(r"\s*\.{3,}\s*")

        self.EXCESS_NEWLINES_PATTERN = re.compile(r"\n{3,}")

    def repair_paragraph_flow(self, text: str) -> str:
        """
        Stitches back single newlines that fragment standard sentences
        while preserving true double-newline paragraph blocks.
        """
        # Split by explicit structural paragraph breaks
        paragraphs = text.split("\n\n")
        cleaned_paragraphs = []

        for para in paragraphs:
            # Replace single internal newlines within a single paragraph with a normal space
            joined_para = para.replace("\n", " ")
            # Collapse multiple spaces down to one
            joined_para = re.sub(r"\s+", " ", joined_para)
            cleaned_paragraphs.append(joined_para.strip())

        return "\n\n".join(cleaned_paragraphs)

    def clean_text(self, text: str) -> str:
        text = self.CITATION_PATTERN.sub("", text)
        text = self.EM_DASH_PATTERN.sub(" - ", text)
        text = self.HAIR_SPACE_PATTERN.sub(" ", text)
        text = self.ELLIPSIS_PATTERN.sub(" ... ", text)

        text = self.repair_paragraph_flow(text)
        text = self.EXCESS_NEWLINES_PATTERN.sub("\n\n", text)

        return text.strip()

    def clean_documents(self, documents: List[Document]) -> List[Document]:
        cleaned_documents = []
        for document in documents:
            cleaned_content = self.clean_text(document.page_content)
            cleaned_documents.append(
                Document(page_content=cleaned_content, metadata=document.metadata)
            )
        return cleaned_documents
