import io
from typing import List

from pypdf import PdfReader


async def extract_text_from_file(file_content: bytes, filename: str)-> str:
    if filename.endswith(".txt"):
        return file_content.decode("utf-8")
    elif filename.endswith(".pdf"):
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text= ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        raise ValueError("Unsupported file format. Use .pdf or .txt")

def chunk_by_fixed_size(text: str, chunk_size: int = 1000, overlap: int = 200)->List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def chunk_by_paragraph(text:str) -> List[str]:
    raw_chunks = text.split("\n\n")
    clean_chunks = [chunk.strip() for chunk in raw_chunks if len(chunk.strip()) > 10]
    return clean_chunks

def process_chunks(text:str, strategy: str) -> List[str]:
    if strategy == "fixed":
        return chunk_by_fixed_size(text)
    elif strategy == "paragraph":
        return chunk_by_paragraph(text)
    else:
        raise ValueError("Invalid strategy. Choose 'fixed' or 'paragraph'.")
