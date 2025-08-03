# D:\DevBuddy\backend\app\services\embedding_service.py

import os
from typing import List, Dict, Any
from loguru import logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.base import Embeddings
from tenacity import retry, wait_random_exponential, stop_after_attempt

class EmbeddingService:
    def __init__(self):
        """
        Initializes the embedding service with a Gemini embedding model.
        The GoogleGenerativeAIEmbeddings class is part of the langchain-google-genai
        package and requires the GOOGLE_API_KEY environment variable.
        """
        # Ensure the GOOGLE_API_KEY is set
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set.")
            raise ValueError("GOOGLE_API_KEY not found. Please set the environment variable.")

        try:
            # We are using the LangChain wrapper for Google Generative AI embeddings
            # This handles the API client creation and embedding generation
            self.embedding_model: Embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key,
            )
            logger.info("Successfully initialized Gemini embedding model.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embedding model: {e}")
            raise RuntimeError("Gemini API key might be missing or invalid.") from e

    # There is no direct equivalent of tiktoken for Gemini models, but the SDK
    # can handle token counting implicitly. The API has a limit of 2048 tokens per
    # individual text input. The LangChain wrapper should handle this.
    # We will remove the `truncate_text` and `count_tokens` methods as they are no
    # longer needed with the `GoogleGenerativeAIEmbeddings` class.

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a single batch of texts with retry logic.
        """
        return await self.embedding_model.aembed_documents(texts)
    
    async def embed_code_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Generates embeddings for a list of code chunks using the initialized
        Gemini embedding model.

        Args:
            chunks: A list of dictionaries, where each dictionary represents a
                    code chunk and contains a 'content' key with the code string.

        Returns:
            A list of lists of floats, where each inner list is the embedding
            vector for a corresponding code chunk.
        """
        if not chunks:
            return []

        # The `GoogleGenerativeAIEmbeddings` class handles batching automatically.
        # We just need to extract the text content from the chunks.
        texts = [self.prepare_chunk_for_embedding(chunk) for chunk in chunks]
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = await self._embed_batch(texts)
            logger.info("Embeddings generation complete.")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError("Embedding generation failed.") from e

    def prepare_chunk_for_embedding(self, chunk: Dict[str, Any]) -> str:
        """Prepare a code chunk for embedding"""
        parts = []
        
        # Add context information
        if chunk.get("file_path"):
            parts.append(f"File: {chunk['file_path']}")
        
        if chunk.get("class_name"):
            parts.append(f"Class: {chunk['class_name']}")
        
        if chunk.get("function_name"):
            parts.append(f"Function: {chunk['function_name']}")
        
        # Add docstring if available
        if chunk.get("docstring"):
            parts.append(f"Documentation: {chunk['docstring']}")
        
        # Add the actual code content
        parts.append(f"Code:\n{chunk['content']}")
        
        return "\n\n".join(parts)