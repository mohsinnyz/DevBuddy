# D:\DevBuddy\backend\app\services\embedding_service.py

import os
from typing import List, Dict, Any
from loguru import logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.base import Embeddings

class EmbeddingService:
    def __init__(self):
        """
        Initializes the embedding service with a Gemini model.
        The GoogleGenerativeAIEmbeddings class is part of the langchain-google-genai
        package and requires the GOOGLE_API_KEY environment variable.
        """
        try:
            # Using Gemini's embedding model for text-to-vector conversion
            # The model name "models/embedding-001" is a standard embedding model
            # provided by Google.
            self.embedding_model: Embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            )
            logger.info("Successfully initialized Gemini embedding model.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embedding model: {e}")
            raise RuntimeError("Gemini API key might be missing or invalid.") from e

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

        # Extract the content from each chunk to create a list of text strings
        texts = [chunk['content'] for chunk in chunks]
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            # Use the asynchronous aembed_documents method for efficiency
            embeddings = await self.embedding_model.aembed_documents(texts)
            logger.info("Embeddings generation complete.")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError("Embedding generation failed.") from e