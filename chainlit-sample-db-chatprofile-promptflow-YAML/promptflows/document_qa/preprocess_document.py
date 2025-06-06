import re
from typing import Dict, List

# For direct usage without promptflow runtime, we don't need the @tool decorator
def preprocess_document(document_content: str, question: str) -> Dict:
    """
    Preprocess the document content by cleaning and structuring it.
    
    Args:
        document_content: Raw document content
        question: User question for context
        
    Returns:
        Processed document structure with chunks and metadata
    """
    
    if not document_content.strip():
        return {
            "chunks": [],
            "total_length": 0,
            "chunk_count": 0,
            "metadata": {"error": "No document content provided"}
        }
    
    # Clean the document content
    cleaned_content = re.sub(r'\s+', ' ', document_content.strip())
    
    # Split into chunks (simple sentence-based chunking)
    sentences = re.split(r'[.!?]+', cleaned_content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Create chunks of approximately 200 words each
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        word_count = len(sentence.split())
        
        if current_word_count + word_count > 200 and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_word_count = word_count
        else:
            current_chunk.append(sentence)
            current_word_count += word_count
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # Create processed document structure
    processed_doc = {
        "chunks": chunks,
        "total_length": len(cleaned_content),
        "chunk_count": len(chunks),
        "metadata": {
            "original_length": len(document_content),
            "sentence_count": len(sentences),
            "processing_status": "success"
        }
    }
    
    return processed_doc 