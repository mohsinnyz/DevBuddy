import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from loguru import logger
import uuid

class QdrantService:
    def __init__(self):
        self.client = None
        self.collection_name = "devbuddy_code_chunks"
        self.embedding_dimension = int(os.getenv("EMBEDDING_DIMENSION", 1536))
        
    async def initialize(self):
        """Initialize Qdrant client and create collection if needed"""
        try:
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key if qdrant_api_key else None
            )
            
            # Check if collection exists, create if not
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                await self.create_collection()
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            raise
    
    async def create_collection(self):
        """Create a new collection for code chunks"""
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_dimension,
                distance=Distance.COSINE
            )
        )
    
    async def store_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Store code chunks with their embeddings"""
        try:
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = str(uuid.uuid4())
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "chunk_id": chunk.get("chunk_id", point_id),
                        "file_path": chunk["file_path"],
                        "function_name": chunk.get("function_name"),
                        "class_name": chunk.get("class_name"),
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                        "content": chunk["content"],
                        "chunk_type": chunk["chunk_type"],
                        "docstring": chunk.get("docstring"),
                        "repo_url": chunk.get("repo_url"),
                        "file_extension": chunk.get("file_extension", ".py")
                    }
                )
                points.append(point)
            
            # Batch insert points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Stored {len(points)} chunks in Qdrant")
            return len(points)
            
        except Exception as e:
            logger.error(f"Failed to store chunks in Qdrant: {e}")
            raise
    
    async def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        repo_url: Optional[str] = None,
        file_path: Optional[str] = None,
        chunk_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar code chunks"""
        try:
            # Build filter conditions
            filter_conditions = []
            
            if repo_url:
                filter_conditions.append(
                    models.FieldCondition(
                        key="repo_url",
                        match=models.MatchValue(value=repo_url)
                    )
                )
            
            if file_path:
                filter_conditions.append(
                    models.FieldCondition(
                        key="file_path",
                        match=models.MatchValue(value=file_path)
                    )
                )
                
            if chunk_type:
                filter_conditions.append(
                    models.FieldCondition(
                        key="chunk_type",
                        match=models.MatchValue(value=chunk_type)
                    )
                )
            
            # Create filter if conditions exist
            search_filter = None
            if filter_conditions:
                search_filter = models.Filter(
                    must=filter_conditions
                )
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "chunk_id": result.payload["chunk_id"],
                    "file_path": result.payload["file_path"],
                    "function_name": result.payload.get("function_name"),
                    "class_name": result.payload.get("class_name"),
                    "content": result.payload["content"],
                    "score": result.score,
                    "metadata": {
                        "start_line": result.payload["start_line"],
                        "end_line": result.payload["end_line"],
                        "chunk_type": result.payload["chunk_type"],
                        "docstring": result.payload.get("docstring")
                    }
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search in Qdrant: {e}")
            raise
    
    async def delete_by_repo(self, repo_url: str):
        """Delete all chunks for a specific repository"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="repo_url",
                                match=models.MatchValue(value=repo_url)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted chunks for repo: {repo_url}")
            
        except Exception as e:
            logger.error(f"Failed to delete chunks for repo {repo_url}: {e}")
            raise
    
    async def search_by_keywords(
        self, 
        keywords: List[str], 
        limit: int = 10,
        repo_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for code chunks containing specific keywords"""
        try:
            # Build filter conditions
            filter_conditions = []
            
            if repo_url:
                filter_conditions.append(
                    models.FieldCondition(
                        key="repo_url",
                        match=models.MatchValue(value=repo_url)
                    )
                )
            
            # Create keyword search conditions
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(
                    models.FieldCondition(
                        key="content",
                        match=models.MatchText(text=keyword)
                    )
                )
            
            if keyword_conditions:
                filter_conditions.append(
                    models.Filter(
                        should=keyword_conditions  # Use 'should' for OR logic
                    )
                )
            
            # Create filter if conditions exist
            search_filter = None
            if filter_conditions:
                search_filter = models.Filter(
                    must=filter_conditions
                )
            
            # Perform search with a dummy vector (we're doing keyword search)
            dummy_vector = [0.0] * self.embedding_dimension
            
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=dummy_vector,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "chunk_id": result.payload["chunk_id"],
                    "file_path": result.payload["file_path"],
                    "function_name": result.payload.get("function_name"),
                    "class_name": result.payload.get("class_name"),
                    "content": result.payload["content"],
                    "score": result.score,
                    "metadata": {
                        "start_line": result.payload["start_line"],
                        "end_line": result.payload["end_line"],
                        "chunk_type": result.payload["chunk_type"],
                        "docstring": result.payload.get("docstring")
                    }
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by keywords in Qdrant: {e}")
            return []

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
