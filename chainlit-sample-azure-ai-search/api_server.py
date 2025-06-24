import os
import mimetypes
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Depends, status, Request, Query, Header
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from azure.storage.blob.aio import BlobClient, BlobServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
AZURE_STORAGE_ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
AZURE_SEARCH_SERVICE_ENDPOINT = os.environ.get("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_API_KEY = os.environ.get("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME")
USE_MANAGED_IDENTITY = os.environ.get("USE_MANAGED_IDENTITY", "false").lower() == "true"

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Global clients
blob_service_client = None
search_client = None

# Comprehensive MIME type mapping
MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".ppt": "application/vnd.ms-powerpoint",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".json": "application/json",
    ".xml": "application/xml",
    ".html": "text/html",
    ".htm": "text/html",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip"
}

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class DocumentAccess(BaseModel):
    doc_id: str
    user_id: str
    access_level: str  # "read", "write", "admin"
    granted_at: datetime

# Fake users database (replace with real database in production)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "disabled": False,
    }
}

# Create FastAPI app
app = FastAPI(
    title="Azure AI Search Document API",
    description="Enhanced document serving API with authentication and document viewers",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_blob_service_client():
    """Get or create Azure Blob Service client"""
    global blob_service_client
    if blob_service_client is None:
        try:
            # Check for service principal credentials
            client_id = os.environ.get("AZURE_CLIENT_ID")
            client_secret = os.environ.get("AZURE_CLIENT_SECRET") 
            tenant_id = os.environ.get("AZURE_TENANT_ID")
            storage_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
            
            if client_id and client_secret and tenant_id:
                # Use service principal authentication
                from azure.identity.aio import ClientSecretCredential
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=credential
                )
                logger.info("Using service principal authentication for blob storage")
                
            elif storage_key:
                # Use storage account key
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=storage_key
                )
                logger.info("Using storage account key authentication for blob storage")
                
            elif USE_MANAGED_IDENTITY:
                # Use managed identity
                credential = DefaultAzureCredential()
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=credential
                )
                logger.info("Using managed identity authentication for blob storage")
                
            else:
                # Fallback to default credential chain
                credential = DefaultAzureCredential()
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=credential
                )
                logger.info("Using default credential chain for blob storage")
                
        except Exception as e:
            logger.error(f"Failed to initialize blob service client: {str(e)}")
            return None
    return blob_service_client

async def get_search_client():
    """Get or create Azure Search client"""
    global search_client
    if search_client is None:
        try:
            if AZURE_SEARCH_API_KEY:
                credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)
            else:
                credential = DefaultAzureCredential()
            
            search_client = SearchClient(
                endpoint=AZURE_SEARCH_SERVICE_ENDPOINT,
                index_name=AZURE_SEARCH_INDEX_NAME,
                credential=credential
            )
        except Exception as e:
            logger.error(f"Failed to initialize search client: {str(e)}")
            return None
    return search_client

def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password"""
    return pwd_context.hash(password)

def get_user(db, username: str):
    """Get user from database"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    """Authenticate user credentials"""
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_flexible(
    request: Request,
    token: Optional[str] = Query(None, description="Bearer token for authentication"),
    authorization: Optional[str] = Header(None)
) -> User:
    """Get current user from either query parameter token or Authorization header"""
    auth_token = None
    
    # Try to get token from query parameter first
    if token:
        auth_token = token
    # Try to get token from Authorization header
    elif authorization and authorization.startswith("Bearer "):
        auth_token = authorization.split(" ")[1]
    
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_blob_client(blob_path: str):
    """Get blob client for specific blob"""
    blob_service = await get_blob_service_client()
    if not blob_service:
        raise HTTPException(status_code=500, detail="Blob service not available")
    
    blob_client = blob_service.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME,
        blob=blob_path
    )
    return blob_client

async def get_blob_path_from_search(doc_id: str) -> Optional[str]:
    """Query Azure AI Search to get blob path for document ID"""
    try:
        client = await get_search_client()
        if not client:
            return None
        
        # Search for document by chunk_id using search query instead of filter
        # since chunk_id is not filterable in the current index
        results = await client.search(
            search_text=f'"{doc_id}"',  # Search for exact chunk_id value
            search_fields=["chunk_id"],  # Only search in chunk_id field
            select=["chunk_id", "metadata_storage_path"],
            top=10  # Get more results to find exact match
        )
        
        async for result in results:
            result_chunk_id = result.get("chunk_id", "")
            # Check for exact match since search might return partial matches
            if result_chunk_id == doc_id:
                storage_path = result.get("metadata_storage_path", "")
                if storage_path:
                    # Extract blob path from full URL
                    # URL format: https://account.blob.core.windows.net/container/blob-path
                    # We need: blob-path (which may include folders)
                    if storage_path.startswith('https://'):
                        # Parse URL to extract blob path after container
                        url_parts = storage_path.split('/')
                        if len(url_parts) >= 5:  # https, '', domain, container, blob-path...
                            # Join everything after container name
                            blob_path = '/'.join(url_parts[4:])  # Skip https://domain/container
                            return blob_path
                    # Fallback: if not a URL, return as-is
                    return storage_path
        
        return None
    except Exception as e:
        logger.error(f"Error getting blob path from search: {str(e)}")
        return None

async def authorize_user(current_user: User, doc_id: str) -> bool:
    """Check if user has access to specific document"""
    # In production, implement proper authorization logic
    # For now, all authenticated users have access to all documents
    # You might check against a permissions database, Azure AD groups, etc.
    
    try:
        # Example authorization checks:
        # 1. Check if user has general document access
        if current_user.disabled:
            return False
        
        # 2. Check document-specific permissions (implement based on your needs)
        # This could involve checking:
        # - User roles/groups
        # - Document metadata
        # - Organizational permissions
        # - Time-based access controls
        
        # For demo purposes, allow all authenticated users
        return True
        
    except Exception as e:
        logger.error(f"Error in authorization check: {str(e)}")
        return False

def get_content_type(blob_path: str) -> str:
    """Determine content type from file extension"""
    _, ext = os.path.splitext(blob_path.lower())
    return MIME_TYPES.get(ext, "application/octet-stream")

# API Endpoints

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user_flexible)):
    """Get current user information"""
    return current_user

@app.get("/api/file")
async def stream_blob(
    doc_id: str,
    request: Request,
    current_user: User = Depends(get_current_user_flexible)
):
    """Stream blob file with authentication and authorization"""
    logger.info(f"File request received: doc_id={doc_id}, user={current_user.username}")
    
    # Get blob path from document ID
    blob_path = await get_blob_path_from_search(doc_id)
    if not blob_path:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Authorize user access to document
    if not await authorize_user(current_user, doc_id):
        raise HTTPException(status_code=403, detail="Unauthorized access to document")
    
    blob_client = await get_blob_client(blob_path)
    
    try:
        # Get blob properties
        props = await blob_client.get_blob_properties()
        content_length = props.size
        content_type = get_content_type(blob_path)
        
        # Handle range requests for video/PDF streaming
        range_header = request.headers.get('Range')
        
        if range_header:
            # Parse range header
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else content_length - 1
            
            # Ensure end doesn't exceed content length
            end = min(end, content_length - 1)
            
            # Download blob with range
            blob_data = await blob_client.download_blob(offset=start, length=end - start + 1)
            content = await blob_data.readall()
            
            headers = {
                'Content-Range': f'bytes {start}-{end}/{content_length}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(len(content)),
                'Content-Type': content_type,
                'Cache-Control': 'max-age=3600',  # Cache for 1 hour
                'Content-Disposition': f'inline; filename={blob_path.split("/")[-1] if "/" in blob_path else blob_path}'
            }
            
            return StreamingResponse(
                iter([content]),
                status_code=206,
                headers=headers
            )
        else:
            # Stream blob content
            async def stream_generator():
                async with blob_client:
                    stream = await blob_client.download_blob()
                    async for chunk in stream.chunks():
                        yield chunk
            
            headers = {
                'Content-Length': str(content_length),
                'Content-Type': content_type,
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'max-age=3600',  # Cache for 1 hour
                'Content-Disposition': f'inline; filename={blob_path.split("/")[-1] if "/" in blob_path else blob_path}'
            }
            
            return StreamingResponse(
                stream_generator(),
                media_type=content_type,
                headers=headers
            )
            
    except Exception as e:
        logger.error(f"Error serving blob file {blob_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@app.get("/api/document/{doc_id}/info")
async def get_document_info(
    doc_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get document information including type and metadata"""
    try:
        # Get blob path from document ID
        blob_path = await get_blob_path_from_search(doc_id)
        if not blob_path:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Authorize user access
        if not await authorize_user(current_user, doc_id):
            raise HTTPException(status_code=403, detail="Unauthorized access to document")
        
        # Get blob properties
        blob_client = await get_blob_client(blob_path)
        props = await blob_client.get_blob_properties()
        
        # Determine file type and extension
        _, ext = os.path.splitext(blob_path.lower())
        content_type = get_content_type(blob_path)
        
        return {
            "doc_id": doc_id,
            "filename": blob_path.split("/")[-1] if "/" in blob_path else blob_path,
            "file_extension": ext,
            "content_type": content_type,
            "size": props.size,
            "last_modified": props.last_modified.isoformat() if props.last_modified else None,
            "blob_path": blob_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting document info: {str(e)}")

@app.get("/auth_demo.html", response_class=HTMLResponse)
async def auth_demo():
    """Serve the authentication demo page"""
    try:
        with open("auth_demo.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Authentication demo page not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Azure AI Search Document API v2.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8001, reload=True) 