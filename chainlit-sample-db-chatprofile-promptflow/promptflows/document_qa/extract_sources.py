from typing import Dict, List
import re

# For direct usage without promptflow runtime, we don't need the @tool decorator
def extract_sources(processed_doc: Dict, context: str, answer: str) -> str:
    """
    Extract and format source information for citations.
    
    Args:
        processed_doc: Preprocessed document structure
        context: Context used for answer generation
        answer: Generated answer
        
    Returns:
        Formatted source citations
    """
    
    try:
        if not processed_doc.get("chunks"):
            return "**Sources:** No document sources available"
        
        # Find which chunks were used in the context
        used_chunks = []
        for i, chunk in enumerate(processed_doc["chunks"]):
            if chunk.strip() in context:
                used_chunks.append(i + 1)  # 1-indexed for user display
        
        # Extract key phrases from answer that might be direct quotes
        # Look for phrases that appear in both answer and context
        answer_sentences = re.split(r'[.!?]+', answer)
        potential_quotes = []
        
        for sentence in answer_sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only consider substantial sentences
                # Check if significant portions appear in context
                words = sentence.lower().split()
                if len(words) >= 5:
                    # Check for phrase matches
                    for i in range(len(words) - 4):
                        phrase = ' '.join(words[i:i+5])
                        if phrase in context.lower():
                            potential_quotes.append(sentence)
                            break
        
        # Format sources section
        sources_text = "**Sources:**\n"
        
        if used_chunks:
            sources_text += f"• Document sections used: {', '.join(map(str, used_chunks))}\n"
        
        # Add metadata about the document
        metadata = processed_doc.get("metadata", {})
        if metadata:
            sources_text += f"• Total document length: {metadata.get('original_length', 'N/A')} characters\n"
            sources_text += f"• Processed into {processed_doc.get('chunk_count', 0)} sections\n"
        
        # Add information about potential direct quotes
        if potential_quotes:
            sources_text += f"• Contains {len(potential_quotes)} potential direct reference(s)\n"
        
        sources_text += "\n*Note: Citations are automatically generated based on document analysis*"
        
        return sources_text
        
    except Exception as e:
        return f"**Sources:** Error extracting source information: {str(e)}" 