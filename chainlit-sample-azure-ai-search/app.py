import os
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, unquote
import mimetypes

import chainlit as cl
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
VECTOR_FIELD_NAME = os.environ.get("VECTOR_FIELD_NAME", "vector")  # Vector field in your Azure AI Search index

AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_API_KEY = os.environ.get("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME")

AZURE_STORAGE_ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")

USE_MANAGED_IDENTITY = os.environ.get("USE_MANAGED_IDENTITY", "false").lower() == "true"

# API Server configuration
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8001")
API_SERVICE_USERNAME = os.environ.get("API_SERVICE_USERNAME", "testuser")
API_SERVICE_PASSWORD = os.environ.get("API_SERVICE_PASSWORD", "secret")

# Global HTTP session for API server communication
http_session = None
api_token = None

# Initialize clients
openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

# Global variables for async clients
search_client = None
blob_service_client = None

async def get_http_session():
    """Get or create aiohttp session"""
    global http_session
    if http_session is None:
        http_session = aiohttp.ClientSession()
    return http_session

async def authenticate_with_api_server():
    """Authenticate with API server and get access token"""
    global api_token
    
    try:
        session = await get_http_session()
        
        # Prepare authentication data
        auth_data = {
            "username": API_SERVICE_USERNAME,
            "password": API_SERVICE_PASSWORD
        }
        
        # Send authentication request
        async with session.post(
            f"{API_SERVER_URL}/token",
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if response.status == 200:
                token_data = await response.json()
                api_token = token_data.get("access_token")
                logger.info("Successfully authenticated with API server")
                return api_token
            else:
                error_text = await response.text()
                logger.error(f"Failed to authenticate with API server: {response.status} - {error_text}")
                return None
                
    except Exception as e:
        logger.error(f"Error authenticating with API server: {str(e)}")
        return None

async def get_authenticated_file_url(doc_id: str) -> Optional[str]:
    """Get authenticated file URL that includes the bearer token"""
    global api_token
    
    # Ensure we have a valid token
    if not api_token:
        api_token = await authenticate_with_api_server()
    
    if not api_token:
        return None
    
    # Create authenticated URL with token
    return f"{API_SERVER_URL}/api/file?doc_id={doc_id}&token={api_token}"

async def stream_file_from_api(doc_id: str) -> Optional[bytes]:
    """Stream file content directly from API server"""
    global api_token
    
    try:
        # Ensure we have a valid token
        if not api_token:
            api_token = await authenticate_with_api_server()
        
        if not api_token:
            return None
        
        session = await get_http_session()
        headers = {"Authorization": f"Bearer {api_token}"}
        
        async with session.get(
            f"{API_SERVER_URL}/api/file?doc_id={doc_id}",
            headers=headers
        ) as response:
            if response.status == 200:
                return await response.read()
            elif response.status == 401:
                # Token might be expired, try to refresh
                logger.info("Token expired, refreshing...")
                api_token = await authenticate_with_api_server()
                if api_token:
                    headers = {"Authorization": f"Bearer {api_token}"}
                    async with session.get(
                        f"{API_SERVER_URL}/api/file?doc_id={doc_id}",
                        headers=headers
                    ) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.read()
                return None
            else:
                logger.error(f"Failed to fetch file: {response.status}")
                return None
                
    except Exception as e:
        logger.error(f"Error streaming file from API: {str(e)}")
        return None

async def get_search_client():
    """Get or create Azure Search client"""
    global search_client
    if search_client is None:
        try:
            from azure.search.documents.aio import SearchClient
            from azure.core.credentials import AzureKeyCredential
            from azure.identity.aio import DefaultAzureCredential
            
            if USE_MANAGED_IDENTITY:
                credential = DefaultAzureCredential()
            else:
                credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)
            
            search_client = SearchClient(
                endpoint=AZURE_SEARCH_ENDPOINT,
                index_name=AZURE_SEARCH_INDEX_NAME,
                credential=credential
            )
        except Exception as e:
            logger.error(f"Failed to initialize search client: {str(e)}")
            return None
    return search_client

async def get_blob_service_client():
    """Get or create Azure Blob Service client"""
    global blob_service_client
    if blob_service_client is None:
        try:
            from azure.storage.blob.aio import BlobServiceClient
            from azure.identity.aio import DefaultAzureCredential
            
            if USE_MANAGED_IDENTITY:
                credential = DefaultAzureCredential()
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=credential
                )
            else:
                # For API key authentication, you would need the storage account key
                # This is typically handled via managed identity in production
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=DefaultAzureCredential()
                )
        except Exception as e:
            logger.error(f"Failed to initialize blob service client: {str(e)}")
            return None
    return blob_service_client

async def generate_query_embedding(query: str) -> List[float]:
    """Generate embeddings for the user query using text-embedding-3-small"""
    try:
        response = openai_client.embeddings.create(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=query
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating query embedding: {str(e)}")
        return []

async def search_documents(query: str, top_k: int = 5, search_type: str = "hybrid") -> List[Dict[str, Any]]:
    """Search for relevant documents using Azure AI Search with vector, text, or hybrid search"""
    try:
        client = await get_search_client()
        if not client:
            return []
        
        # Generate query embedding for vector search
        query_embedding = await generate_query_embedding(query)
        if not query_embedding and search_type in ["vector", "hybrid"]:
            logger.warning("Failed to generate query embedding, falling back to text search")
            search_type = "text"
        
        # Configure search based on type
        if search_type == "vector":
            # Pure vector search
            from azure.search.documents.models import VectorizedQuery
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k,
                fields=VECTOR_FIELD_NAME
            )
            results = await client.search(
                search_text=None,
                vector_queries=[vector_query],
                top=top_k,
                select=["chunk_id", "title", "chunk", "metadata_storage_path", "metadata_content_type", "metadata_storage_name"]
            )
        elif search_type == "hybrid":
            # Hybrid search (text + vector)
            from azure.search.documents.models import VectorizedQuery
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k,
                fields=VECTOR_FIELD_NAME
            )
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=top_k,
                select=["chunk_id", "title", "chunk", "metadata_storage_path", "metadata_content_type", "metadata_storage_name"],
                search_mode="any",
                query_type="semantic" if "semantic" in AZURE_SEARCH_INDEX_NAME.lower() else "simple"
            )
        else:
            # Pure text search (fallback)
            results = await client.search(
                search_text=query,
                top=top_k,
                select=["chunk_id", "title", "chunk", "metadata_storage_path", "metadata_content_type", "metadata_storage_name"],
                search_mode="any",
                query_type="semantic" if "semantic" in AZURE_SEARCH_INDEX_NAME.lower() else "simple"
            )
        
        documents = []
        async for result in results:
            documents.append({
                "chunk_id": result.get("chunk_id", ""),
                "title": result.get("title", ""),
                "content": result.get("chunk", ""),  # Using 'chunk' field from index
                "metadata_storage_path": result.get("metadata_storage_path", ""),
                "metadata_content_type": result.get("metadata_content_type", ""),
                "metadata_storage_name": result.get("metadata_storage_name", ""),
                "score": result.get("@search.score", 0.0)
            })
        
        return documents
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return []

def generate_response_with_citations(query: str, documents: List[Dict[str, Any]]) -> str:
    """Generate response using OpenAI with document context and citations"""
    if not documents:
        return "I couldn't find any relevant documents to answer your question."
    
    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"[Source {i}] Title: {doc['title']}\nContent: {doc['content'][:500]}...")
    
    context = "\n\n".join(context_parts)
    
    # Create system prompt with context
    system_prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context documents. 

CRITICAL CITATION REQUIREMENT: You MUST ONLY use citations in this exact format: [Source 1], [Source 2], [Source 3], etc.

Context documents:
{context}

STRICT CITATION RULES - NO EXCEPTIONS:
- ONLY use: [Source 1], [Source 2], [Source 3]
- NEVER use: [filename.pdf], [document-name], or any other format
- NEVER include URLs, file names, or document names in citations
- Example: "The revenue was $100M [Source 1] while costs were $50M [Source 2]."

VIOLATION EXAMPLES (DO NOT DO THIS):
❌ [annual-report-2024.pdf]
❌ [document-name]
❌ filename.pdf
❌ (Source 1)

CORRECT EXAMPLES:
✅ [Source 1]
✅ [Source 2]  
✅ [Source 3]

Instructions:
- Base your answer primarily on the provided context
- Include [Source X] citations throughout your response
- If the context doesn't contain enough information, mention this limitation
- Be concise but comprehensive
"""

    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    try:
        response = openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=conversation_history,
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"I encountered an error while generating the response: {str(e)}"

async def format_response_with_clickable_citations(response_text: str, documents: List[Dict[str, Any]]) -> str:
    """Convert [Source X] citations to clickable document links with authentication"""
    formatted_response = response_text
    
    # Only replace standard [Source X] citations - no backup handling to avoid conflicts
    for i, doc in enumerate(documents, 1):
        source_pattern = f"[Source {i}]"
        if source_pattern in formatted_response:
            doc_id = doc.get('chunk_id', '')
            storage_name = doc.get('metadata_storage_name', f"Document {i}")
            
            # Create authenticated link to API server for document viewing
            if doc_id:
                try:
                    # Get authenticated URL with token
                    auth_url = await get_authenticated_file_url(doc_id)
                    if auth_url:
                        clickable_link = f"[{storage_name}]({auth_url})"
                        formatted_response = formatted_response.replace(source_pattern, clickable_link)
                    else:
                        # Fallback to document name only if authentication fails
                        formatted_response = formatted_response.replace(source_pattern, f"**{storage_name}**")
                except Exception as e:
                    logger.error(f"Error creating authenticated link for {doc_id}: {str(e)}")
                    # Fallback to document name only
                    formatted_response = formatted_response.replace(source_pattern, f"**{storage_name}**")
    
    return formatted_response

# Chainlit event handlers
@cl.on_chat_start
async def start():
    """Initialize the chat session and send a welcome message."""
    # Initialize conversation history in user session
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": "You are a helpful AI assistant with access to a document knowledge base."}
    ])
    
    welcome_message = """
# Welcome to Enhanced Azure AI Search Assistant! 🔍✨

I'm your AI assistant powered by **Azure OpenAI**, **Azure AI Search**, and **Azure Blob Storage**. I use **vector search with text-embedding-3-small** to find the most relevant information across your document knowledge base and provide intelligent responses with clickable citations.

## 🎯 **What I Can Do:**
- 🔍 **Vector Search** - Use text-embedding-3-small to find semantically similar content
- ⚡ **Hybrid Search** - Combine vector search with traditional text search for best results
- 💬 **Contextual Answers** - Provide detailed responses based on your knowledge base
- 📋 **Smart Citations** - Reference source documents with clickable links
- 📄 **Document Access** - View PDFs, Word docs, Excel files, and more!

## 🚀 **Two Usage Options:**

### **Option 1: Basic Search (Current Mode)**
- ✅ **Ready to use** - Ask questions and get intelligent answers
- ✅ **Document citations** - See which documents contain the information
- ℹ️ **Note**: Citations show as text links (no document viewer)

### **Option 2: Enhanced with Document Viewers**
For the full experience with in-app PDF/Word/Excel viewers:
```bash
# Terminal 1: Start enhanced API server
python api_server.py

# Terminal 2: Keep this Chainlit app running
chainlit run app.py
```
- ✅ **Everything from Option 1** plus:
- ✅ **In-app document viewers** - Click citations to view documents instantly
- ✅ **Secure access** - Automatic authentication (no manual login needed)
- ✅ **Advanced features** - PDF navigation, Word rendering, Excel tables

## 💡 **Getting Started:**
Just ask me any question about your documents! I'll search the knowledge base and provide relevant information with proper citations.

**Try asking:**
- "What is the company's revenue for 2024?"
- "Show me the key risks mentioned in the annual report"
- "What are the main strategic initiatives?"

How can I help you today?
    """
    
    await cl.Message(
        content=welcome_message,
        author="AI Assistant",
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages with Azure AI Search integration"""
    user_message = message.content
    
    # Create a message placeholder for loading state
    msg = cl.Message(content="🔍 Searching knowledge base...", author="AI Assistant")
    await msg.send()
    
    try:
        # Search for relevant documents using vector search
        await msg.stream_token("\n📖 Analyzing documents with vector search...")
        documents = await search_documents(user_message, top_k=15, search_type="hybrid")
        
        if not documents:
            msg.content = "I couldn't find any relevant documents to answer your question. Could you try rephrasing or asking about a different topic?"
            await msg.update()
            return
        
        # Generate response with citations
        await msg.stream_token("\n💭 Generating response...")
        response_text = generate_response_with_citations(user_message, documents)
        
        # Format response with clickable citations
        formatted_response = await format_response_with_clickable_citations(response_text, documents)
        
        # Add document sources section with authenticated URLs (deduplicated)
        sources_section = "\n\n---\n\n## 📚 Sources\n\n"
        
        # Deduplicate documents by storage name to avoid showing same document multiple times
        unique_docs = {}
        for doc in documents:
            storage_name = doc.get('metadata_storage_name', 'Unknown Document')
            if storage_name not in unique_docs:
                unique_docs[storage_name] = doc
        
        # Show unique documents (max 3)
        for i, (storage_name, doc) in enumerate(list(unique_docs.items())[:3], 1):
            title = doc.get('title', 'Untitled')
            doc_id = doc.get('chunk_id', '')
            
            if doc_id:
                try:
                    # Get authenticated URL with token
                    auth_url = await get_authenticated_file_url(doc_id)
                    if auth_url:
                        sources_section += f"{i}. [{storage_name}]({auth_url}) - {title}\n"
                    else:
                        sources_section += f"{i}. **{storage_name}** - {title}\n"
                except Exception as e:
                    logger.error(f"Error creating authenticated source link for {doc_id}: {str(e)}")
                    sources_section += f"{i}. **{storage_name}** - {title}\n"
            else:
                sources_section += f"{i}. **{storage_name}** - {title}\n"
        
        final_response = formatted_response + sources_section
        
        # Update the message with the final response
        msg.content = final_response
        await msg.update()
        
        # Update conversation history
        conversation_history = cl.user_session.get("conversation_history", [])
        conversation_history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": final_response}
        ])
        cl.user_session.set("conversation_history", conversation_history)
        
    except Exception as e:
        error_message = f"I encountered an error while processing your request: {str(e)}"
        msg.content = error_message
        await msg.update()
        logger.error(f"Error in main handler: {str(e)}")

if __name__ == "__main__":
    # This will be used for direct chainlit run
    pass
