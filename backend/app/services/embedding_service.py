# D:\DevBuddy\backend\app\services\embedding_service.py
import os
import asyncio
from typing import List, Dict, Any
from loguru import logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings
from tenacity import retry, wait_random_exponential, stop_after_attempt

class EmbeddingService:
    def __init__(self):
        """
        Initializes the embedding service with a Gemini embedding model.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set.")
            raise ValueError("GOOGLE_API_KEY not found. Please set the environment variable.")

        try:
            self.embedding_model: Embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key,
                task_type="retrieval_document",
                title="code_chunk"
            )
            logger.info("Successfully initialized Gemini embedding model.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embedding model: {e}")
            raise RuntimeError("Gemini API key might be missing or invalid.") from e

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _embed_batch_sync(self, texts: List[str]) -> List[List[float]]:
        """
        Synchronous batch embedding call, wrapped for async execution.
        """
        return self.embedding_model.embed_documents(texts)

    async def embed_code_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Embeds code chunks asynchronously.
        """
        if not chunks:
            return []

        texts = [self.prepare_chunk_for_embedding(chunk) for chunk in chunks]

        try:
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            # Run the synchronous method in a thread pool
            embeddings = await asyncio.to_thread(self._embed_batch_sync, texts)
            logger.info("Embeddings generation complete.")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError("Embedding generation failed.") from e

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _embed_query_sync(self, text: str) -> List[float]:
        """
        Synchronous single query embedding call, wrapped for async execution.
        """
        return self.embedding_model.embed_query(text)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding vector for a single query text asynchronously.
        This is used by the Retriever Agent for user queries.
        """
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")
        try:
            logger.info("Generating embedding for single query...")
            # Run the synchronous method in a thread pool
            embedding = await asyncio.to_thread(self._embed_query_sync, text)
            logger.info("Single query embedding generated.")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate single query embedding: {e}")
            raise RuntimeError("Single query embedding generation failed.") from e

    def prepare_chunk_for_embedding(self, chunk: Dict[str, Any]) -> str:
        """Formats a code chunk with metadata for embedding"""
        parts = []

        if chunk.get("file_path"):
            parts.append(f"File: {chunk['file_path']}")

        if chunk.get("class_name"):
            parts.append(f"Class: {chunk['class_name']}")

        if chunk.get("function_name"):
            parts.append(f"Function: {chunk['function_name']}")

        if chunk.get("docstring"):
            parts.append(f"Documentation: {chunk['docstring']}")

        parts.append(f"Code:\n{chunk['content']}")

        return "\n\n".join(parts)