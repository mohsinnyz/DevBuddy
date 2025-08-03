import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
import asyncio
from loguru import logger
import tiktoken

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.max_tokens = 8192  # Max tokens for embedding model
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def truncate_text(self, text: str, max_tokens: int = None) -> str:
        """Truncate text to fit within token limit"""
        if max_tokens is None:
            max_tokens = self.max_tokens
            
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
            
        # Truncate and decode back to text
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Truncate text if too long
            text = self.truncate_text(text)
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        try:
            embeddings = []
            
            # Process in batches to avoid rate limits
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Truncate texts in batch
                batch = [self.truncate_text(text) for text in batch]
                
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
                    
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
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
    
    async def embed_code_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for code chunks"""
        try:
            # Prepare texts for embedding
            texts = [self.prepare_chunk_for_embedding(chunk) for chunk in chunks]
            
            # Generate embeddings
            embeddings = await self.generate_embeddings_batch(texts)
            
            logger.info(f"Generated embeddings for {len(chunks)} code chunks")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to embed code chunks: {e}")
            raise
