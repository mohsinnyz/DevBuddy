#D:\DevBuddy\backend\app\main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from loguru import logger

from app.routers import ingest, chat, health
from app.services.qdrant_service import QdrantService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("logs/devbuddy.log", rotation="10 MB", level=os.getenv("LOG_LEVEL", "INFO"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting DevBuddy backend...")
    
    # Initialize Qdrant service
    qdrant_service = QdrantService()
    app.state.qdrant_service = qdrant_service
    
    logger.info("DevBuddy backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DevBuddy backend...")

# Create FastAPI app
app = FastAPI(
    title="DevBuddy API",
    description="Multi-Agent RAG Chatbot for GitHub Repository Analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(ingest.router, prefix="/api", tags=["ingestion"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DevBuddy API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )
