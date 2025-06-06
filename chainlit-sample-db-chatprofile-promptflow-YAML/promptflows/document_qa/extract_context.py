from typing import Dict, List, Any
import re

# For direct usage without promptflow runtime, we don't need the @tool decorator
def extract_context(processed_doc: Dict, question: str, chat_history: List[Dict[str, Any]]) -> Dict:
    """
    Extract relevant context from processed document based on the question.
    
    Args:
        processed_doc: Preprocessed document structure
        question: User question
        chat_history: Previous conversation history
        
    Returns:
        Dictionary with extracted context and formatted history
    """
    
    if not processed_doc.get("chunks"):
        return {
            "context": "No document content available for analysis.",
            "relevant_chunks": [],
            "formatted_history": "",
            "relevance_score": 0.0
        }
    
    # Simple keyword-based relevance scoring
    question_words = set(re.findall(r'\b\w+\b', question.lower()))
    
    # Score each chunk based on keyword overlap
    chunk_scores = []
    for i, chunk in enumerate(processed_doc["chunks"]):
        chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
        overlap = len(question_words.intersection(chunk_words))
        score = overlap / len(question_words) if question_words else 0
        chunk_scores.append((i, chunk, score))
    
    # Sort by relevance score
    chunk_scores.sort(key=lambda x: x[2], reverse=True)
    
    # Take top 3 most relevant chunks
    relevant_chunks = chunk_scores[:3]
    context_pieces = [chunk[1] for chunk in relevant_chunks if chunk[2] > 0]
    
    # If no relevant chunks found, use first few chunks
    if not context_pieces:
        context_pieces = processed_doc["chunks"][:2]
    
    # Combine context
    context = "\n\n".join(context_pieces)
    
    # Format chat history
    formatted_history = ""
    if chat_history:
        formatted_history = "\n\nPrevious conversation context:\n"
        for msg in chat_history[-3:]:  # Use last 3 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_history += f"{role.title()}: {content}\n"
    
    return {
        "context": context,
        "relevant_chunks": [{"index": chunk[0], "score": chunk[2]} for chunk in relevant_chunks[:3]],
        "formatted_history": formatted_history,
        "relevance_score": max([chunk[2] for chunk in relevant_chunks[:3]]) if relevant_chunks else 0.0
    } 