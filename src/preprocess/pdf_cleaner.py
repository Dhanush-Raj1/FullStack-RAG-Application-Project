import re
from typing import List

from src.models.document import Document

class PDFCleaner: 

    HEADER_FOOTER_PATTERNS = [
        re.compile(r"\d{1,2}/\d{1,2}/\d{2},\s+\d{1,2}:\d{2}\s+[AP]M"),  # Timestamps
        re.compile(r"MacBook Air \(13-inch, M5\) - Tech Specs - Apple Support \(IN\)"),  # Page titles
        re.compile(r"https?://\S+"),  # URLs
        re.compile(r"\b\d+/\d+\b"),  # Page counters (e.g., 1/7)
    ]

    IMAGE_PATTERN = re.compile(r"\**==> picture.*?omitted <==\**")
    FOOTNOTE_PATTERN = re.compile(r"\b([A-Za-z]{5,})(\d{1,2})\b")  # e.g., Storage1, Power3

    TRAILING_WS_PATTERN = re.compile(r"[ \t]+$", flags=re.MULTILINE)
    EXCESS_LINES_PATTERN = re.compile(r"\n{3,}")

    BROKEN_WORDS = {
        "Con fig ure": "Configure",
        "En viron men tal": "Environmental",
        "Accessi bility": "Accessibility",
    }

    FOOTER_NOISE_PATTERNS = [
        re.compile(p) for p in [
            r"\**Helpful\?\** Yes No",
            r"Support MacBook Air.*",
            r"Copyright © .*",
            r"Privacy Policy",
            r"Terms of Use",
            r"Sales Policy",
            r"Site Map",
            r"\bIndia\b",
        ]
    ]
    
    def remove_headers_and_footers(self, text: str) -> str:
        """Remove repeated PDF header/footer noise."""
        for pattern in self.HEADER_FOOTER_PATTERNS:
            text = pattern.sub("", text)
        return text

    def remove_image_placeholders(self, text: str) -> str:
        """Remove picture omitted tags."""
        return self.IMAGE_PATTERN.sub("", text)
    
    def fix_footnote_artifacts(self, text: str) -> str:
        """Fix merged footnote/superscript artifacts conservatively (e.g., Storage1 -> Storage)."""
        return self.FOOTNOTE_PATTERN.sub(r"\1", text)
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving markdown structure."""
        text = self.TRAILING_WS_PATTERN.sub("", text)
        text = self.EXCESS_LINES_PATTERN.sub("\n\n", text)
        return text.strip()

    def fix_broken_words(self, text: str) -> str:
        """Fix common OCR-style broken words conservatively."""
        for broken, fixed in self.BROKEN_WORDS.items():
            text = text.replace(broken, fixed)
        return text

    def remove_footer_noise(self, text: str) -> str:
        """Remove remaining website footer artifacts specifically at 7th page."""
        for pattern in self.FOOTER_NOISE_PATTERNS:
            text = pattern.sub("", text)
        return text

    def clean_text(self, text: str) -> str:
        """Apply full text cleaning pipeline."""
        text = self.remove_headers_and_footers(text)
        text = self.remove_image_placeholders(text)
        text = self.fix_broken_words(text)
        text = self.normalize_whitespace(text)
        text = self.remove_footer_noise(text)
        text = self.fix_footnote_artifacts(text)
        return text


    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """Clean a list of Document objects."""

        cleaned_documents: List[Document] = []

        for document in documents:
            cleaned_content = self.clean_text(document.page_content)
            cleaned_document = Document(
                page_content=cleaned_content,
                metadata=document.metadata
            )
            cleaned_documents.append(cleaned_document)

        return cleaned_documents

