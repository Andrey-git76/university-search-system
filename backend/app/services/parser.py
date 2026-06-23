import io
import pdfplumber
from docx import Document
import uuid
import logging

logger = logging.getLogger(__name__)


class DocumentParser:
    
    @staticmethod
    async def parse_pdf(file_content: bytes) -> list:
        pages_text = []
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_text.append({
                            "page": page_num,
                            "text": text.strip()
                        })
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            raise
        return pages_text
    
    @staticmethod
    async def parse_docx(file_content: bytes) -> list:
        try:
            doc = Document(io.BytesIO(file_content))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs)
            return [{"page": 1, "text": full_text}]
        except Exception as e:
            logger.error(f"DOCX parsing error: {str(e)}")
            raise
    
    @staticmethod
    def chunk_pages(pages: list, chunk_size: int = 1000, overlap: int = 100) -> list:
        chunks = []
        for page_data in pages:
            text = page_data["text"]
            words = text.split()
            
            i = 0
            while i < len(words):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "page": page_data["page"],
                    "text": chunk_text
                })
                i += chunk_size - overlap
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks