import re 


EXTRACTION_PATTERN = [
    re.compile(r"(?i)what (is|are) your (system prompt|api key|env(ironment)? variables?)"),
    re.compile(r"(?i)print (your|the) (config|environment|secret)"),
    re.compile(r"(?i)show me (your|the) (source code|\.env|configuration)"),
    re.compile(r"(?i)dump (the )?(database|vector store|index)"),
    re.compile(r"(?i)list all (sessions|users|uploaded files) (on|in) (the|your) server"),

    ]

class DataExtractionDetector:
    def scan(self, text: str) -> bool:
        for pattern in EXTRACTION_PATTERN:
            if pattern.search(text):
                return 
            


