import re
from typing import Union

# For direct usage without promptflow runtime, we don't need the @tool decorator
def calculate_relevance(question: str, answer: str, context: str) -> str:
    """
    Calculate a relevance score for the answer based on question-answer-context alignment.
    
    Args:
        question: User question
        answer: Generated answer
        context: Document context used
        
    Returns:
        Relevance score as a formatted string with explanation
    """
    
    try:
        # Extract key terms from question
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        
        # Remove common stop words for better relevance calculation
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        question_words = question_words - stop_words
        answer_words = answer_words - stop_words
        context_words = context_words - stop_words
        
        # Calculate different relevance metrics
        
        # 1. Question-Answer overlap
        qa_overlap = len(question_words.intersection(answer_words))
        qa_score = qa_overlap / len(question_words) if question_words else 0
        
        # 2. Answer-Context overlap
        ac_overlap = len(answer_words.intersection(context_words))
        ac_score = ac_overlap / len(answer_words) if answer_words else 0
        
        # 3. Question-Context overlap  
        qc_overlap = len(question_words.intersection(context_words))
        qc_score = qc_overlap / len(question_words) if question_words else 0
        
        # Combined relevance score (weighted average)
        overall_score = (qa_score * 0.4 + ac_score * 0.4 + qc_score * 0.2)
        
        # Convert to percentage
        relevance_percentage = round(overall_score * 100, 1)
        
        # Determine relevance category
        if relevance_percentage >= 70:
            category = "High"
        elif relevance_percentage >= 50:
            category = "Medium"
        else:
            category = "Low"
        
        # Create relevance report
        relevance_report = f"**Relevance: {relevance_percentage}% ({category})**\n"
        relevance_report += f"Q-A alignment: {round(qa_score * 100, 1)}%, "
        relevance_report += f"Context grounding: {round(ac_score * 100, 1)}%"
        
        return relevance_report
        
    except Exception as e:
        return f"Relevance calculation error: {str(e)}" 