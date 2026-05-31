import re
from typing import List

from src.models.document import Document


class MarkdownCleaner:
    def __init__(self):
        # Remove boilerplate at the start of files
        self.BOILERPLATE_PATTERN = re.compile(
            r"^>\s*For clean Markdown.*\n"
            r"^>\s*For a complete documentation index.*\n"
            r"^>\s*For full documentation content.*\n"
            r"^>\s*For AI client integration.*\n",
            flags=re.MULTILINE,
        )

        # Remove specific navigation/footer sections 
        self.NAVIGATION_SECTION_PATTERN = re.compile(
            r"^##\s+(?:Next Steps|Related topics)\s*\n(?:(?!^##\s+).)*",
            flags=re.MULTILINE | re.DOTALL,
        )

        # Remove Mermaid code blocks 
        self.MERMAID_PATTERN = re.compile(r"```mermaid\n.*?```\n?", flags=re.DOTALL)

        # Extract caption from image tag: ![Caption](url) -> Caption
        self.IMAGE_PATTERN = re.compile(r"!\[([^\]]*)]\([^\)]+\)")

        # Extract anchor text from markdown links: [Anchor](url) -> Anchor
        self.LINK_PATTERN = re.compile(r"\[([^\]]+)]\([^\)]+\)")

        # Normalize definition lists
        self.DEFINITION_LIST_PATTERN = re.compile(
            r"^([^\n]+)\n:\s*(.+)$", flags=re.MULTILINE
        )

        # Remove leading blockquote markers
        self.BLOCKQUOTE_PATTERN = re.compile(r"^\s*>\s*", flags=re.MULTILINE)

        # Cleans excess vertical whitespace
        self.EXCESS_NEWLINES_PATTERN = re.compile(r"\n{3,}")

    def repair_table_line_breaks(self, text: str) -> str:
        """
        Ensures that markdown table structures fragmented across newlines
        are re-assembled into continuous lines for proper markdown splitting.
        """
        lines = text.splitlines()
        repaired_lines = []
        in_table_zone = False

        for line in lines:
            stripped = line.strip()
            # Detect table rows or markdown table dividers
            if stripped.startswith("|") or (in_table_zone and stripped.endswith("|")):
                # Check if it's a divider row or complete row closure
                if (
                    stripped.startswith("|")
                    and stripped.endswith("|")
                    and len(repaired_lines) > 0
                    and repaired_lines[-1].strip().endswith("|")
                ):
                    # If the previous line didn't close its row or if this line continues a row fragment
                    if "---" in stripped:
                        in_table_zone = True
                        repaired_lines.append(line)
                    else:
                        # Append directly or fix dangling layout
                        repaired_lines.append(line)
                elif in_table_zone and not repaired_lines[-1].strip().endswith("|"):
                    # Join the line fragment to clean up internal string splits
                    repaired_lines[-1] = repaired_lines[-1].rstrip() + " " + stripped
                else:
                    repaired_lines.append(line)
                in_table_zone = True
            else:
                repaired_lines.append(line)
                in_table_zone = False

        return "\n".join(repaired_lines)

    def clean_text(self, text: str) -> str:
        text = self.BOILERPLATE_PATTERN.sub("", text)
        text = self.NAVIGATION_SECTION_PATTERN.sub("", text)
        text = self.MERMAID_PATTERN.sub("", text)

        text = self.IMAGE_PATTERN.sub(r"\1", text)
        text = self.LINK_PATTERN.sub(r"\1", text)
        text = self.DEFINITION_LIST_PATTERN.sub(r"\1: \2", text)
        text = self.BLOCKQUOTE_PATTERN.sub("", text)

        text = self.repair_table_line_breaks(text)

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
