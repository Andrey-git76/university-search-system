"""Text chunking utilities."""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text
        chunk_size: Maximum characters per chunk
        overlap: Overlap in characters between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Split by paragraphs first for better semantic chunks
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph exceeds chunk size, save current chunk
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap by keeping last words
            words = current_chunk.split()
            current_chunk = " ".join(words[-overlap:]) if len(current_chunk) > overlap else ""
        
        current_chunk += para + "\n"
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # If no chunks were created (text too short), return original text
    if not chunks:
        chunks = [text]
    
    return chunks