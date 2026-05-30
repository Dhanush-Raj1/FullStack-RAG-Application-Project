from src.loaders.pdf_loader import load_pdf
from src.preprocess.pdf_cleaner import PDFCleaner
from src.utils.config import PDF_DIRECTORY

cleaner = PDFCleaner()

pdf_docs = load_pdf(file_path=PDF_DIRECTORY)
cleaned_docs = cleaner.clean_documents(pdf_docs)