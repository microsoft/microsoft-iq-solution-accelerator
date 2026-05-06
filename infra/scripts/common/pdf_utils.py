"""
PDF processing and text chunking utilities for Foundry deployment scripts.
"""

import logging
import re
from datetime import datetime
from pathlib import Path

# Module-level logger — inherits configuration from the root logger.
logger = logging.getLogger(__name__)

# Default chunking parameters matching the original script's behaviour.
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def extract_pages_from_pdf(filepath) -> list:
    """Extract text content from each page of a PDF file.

    Args:
        filepath: Path to the PDF file.

    Returns:
        List of ``(page_number, text)`` tuples (1-indexed page numbers).
        Pages with no extractable text are omitted.
    """
    from pypdf import PdfReader

    reader = PdfReader(filepath)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append((i + 1, text.strip()))
    return pages


def split_into_sentences(text: str) -> list:
    """Split text into sentences, preserving sentence boundaries.

    Args:
        text: Input text.

    Returns:
        List of sentence strings.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text_by_sentences(
    text: str,
    max_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list:
    """Split text into chunks that respect sentence boundaries.

    Chunks will not exceed ``max_size`` characters and will not cut
    mid-sentence. Overlap is applied by including trailing sentences
    from the previous chunk at the start of the next.

    Args:
        text: Input text to chunk.
        max_size: Maximum chunk size in characters.
        overlap: Target overlap in characters between consecutive chunks.

    Returns:
        List of text chunk strings.
    """
    sentences = split_into_sentences(text)

    if not sentences:
        return [text] if text.strip() else []

    chunks = []
    current_chunk = []
    current_length = 0
    overlap_sentences = []

    for sentence in sentences:
        sentence_len = len(sentence)

        # If a single sentence exceeds max_size, include it as its own chunk.
        if sentence_len > max_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk[:]
            chunks.append(sentence)
            current_chunk = []
            current_length = 0
            overlap_sentences = []
            continue

        potential_length = current_length + sentence_len + (1 if current_chunk else 0)

        if potential_length > max_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            overlap_text_len = sum(len(s) for s in overlap_sentences) + len(overlap_sentences)
            if overlap_text_len < overlap and overlap_sentences:
                current_chunk = overlap_sentences[:]
                current_length = overlap_text_len
            else:
                current_chunk = []
                current_length = 0

        current_chunk.append(sentence)
        current_length += sentence_len + (1 if len(current_chunk) > 1 else 0)
        overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk[:]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def process_pdfs_to_documents(pdf_files: list, blob_urls: dict) -> list:
    """Process a list of PDF files into search-ready document chunks.

    For each PDF:
    - Extract text from each page.
    - Split page text into sentence-boundary-aware chunks.
    - Attach blob storage URL metadata for citation support.

    Args:
        pdf_files: List of PDF file paths (``str`` or ``Path``).
        blob_urls: Mapping of ``filename → blob URL`` from a prior blob upload.

    Returns:
        List of document dicts ready to be uploaded to an Azure AI Search index.
    """
    documents = []
    for pdf_path in pdf_files:
        pdf_path = Path(pdf_path)
        logger.info(f"      Processing: {pdf_path.name}")
        file_stats = pdf_path.stat()
        blob_url = blob_urls.get(pdf_path.name, "")

        pages = extract_pages_from_pdf(pdf_path)
        logger.debug(f"         Extracted {len(pages)} page(s) from {pdf_path.name}")

        for page_num, page_text in pages:
            chunks = chunk_text_by_sentences(page_text)
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{pdf_path.stem}_p{page_num}_c{chunk_idx}"
                page_url = f"{blob_url}#page={page_num}" if blob_url else ""
                documents.append({
                    "id": doc_id,
                    "content": chunk,
                    "title": pdf_path.stem.replace("_", " ").title(),
                    "source": pdf_path.name,
                    "page_number": page_num,
                    "chunk_id": chunk_idx,
                    "blob_url": blob_url,
                    "page_url": page_url,
                    "file_size": file_stats.st_size,
                    "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat() + 'Z',
                })
    return documents
