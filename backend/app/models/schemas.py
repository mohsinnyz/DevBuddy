#D:\DevBuddy\backend\app\models\schemas.py

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import HttpUrl

class IngestionStatus(str, Enum):
    PENDING = "pending"
    CLONING = "cloning"
    PARSING = "parsing"
    EMBEDDING = "embedding"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"

class IngestionRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"
    include_patterns: Optional[List[str]] = ["*.py"]
    exclude_patterns: Optional[List[str]] = ["__pycache__", "*.pyc", ".git"]

class IngestionResponse(BaseModel):
    task_id: str
    status: IngestionStatus
    message: str
    repo_url: HttpUrl

class IngestionStatusResponse(BaseModel):
    task_id: str
    status: IngestionStatus
    progress: Optional[float] = None
    message: str
    files_processed: Optional[int] = None
    total_files: Optional[int] = None
    chunks_created: Optional[int] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    repo_url: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = []
    max_context_chunks: Optional[int] = 10

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    agent_used: str
    processing_time: float

class CodeChunk(BaseModel):
    chunk_id: str
    file_path: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    start_line: int
    end_line: int
    content: str
    chunk_type: str  # "function", "class", "module"
    docstring: Optional[str] = None

class SearchResult(BaseModel):
    chunk_id: str
    file_path: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    content: str
    score: float
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    timestamp: str
