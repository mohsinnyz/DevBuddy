# D:\DevBuddy\backend\app\services\qdrant_service.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
import os
import uuid
import logging

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self, collection_name: str = "code_chunks", vector_size: int = 768):
        local_qdrant_path = os.path.join(os.getcwd(), "local_qdrant_db")
        self.client = AsyncQdrantClient(path=local_qdrant_path)
        self.collection_name = collection_name
        self.vector_size = vector_size

    async def initialize(self):
        try:
            await self.client.get_collection(self.collection_name)
        except Exception:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
        logger.info("Qdrant service initialized and collection checked.")

    async def add_embeddings(self, ids: List[str], embeddings: List[List[float]], metadata: List[dict]):
        points = [
            PointStruct(id=uid, vector=vector, payload=data)
            for uid, vector, data in zip(ids, embeddings, metadata)
        ]
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def store_chunks(self, embeddings: List[List[float]], metadata_list: List[dict]):
        points = [
            PointStruct(id=str(uuid.uuid4()), vector=embedding, payload=metadata)
            for embedding, metadata in zip(embeddings, metadata_list)
        ]
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def query_similar_chunks(self, query_vector: List[float], top_k: int = 5, query_filter: Filter = None):
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )
        return results

    async def search_similar(self, query_vector: List[float], limit: int = 10, repo_url: Optional[str] = None) -> List[Dict[str, Any]]:
        query_filter = None
        if repo_url:
            query_filter = Filter(
                must=[FieldCondition(key="repo_url", match=MatchValue(value=repo_url))]
            )

        results = await self.query_similar_chunks(query_vector, top_k=limit, query_filter=query_filter)
        return [
            {"chunk_id": r.id, "score": r.score, **(r.payload or {})}
            for r in results
        ]

    async def search_by_keywords(self, keywords: List[str], limit: int = 5, repo_url: Optional[str] = None) -> List[Dict[str, Any]]:
        must_conditions = [
            FieldCondition(key="content", match=MatchValue(value=kw)) for kw in keywords
        ]
        if repo_url:
            must_conditions.append(FieldCondition(key="repo_url", match=MatchValue(value=repo_url)))
            
        query_filter = Filter(must=must_conditions)

        results, _ = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit=limit,
        )

        return [
            {"chunk_id": r.id, "score": 1.0, **(r.payload or {})}
            for r in results
        ]

    async def delete_all(self):
        await self.client.delete_collection(self.collection_name)
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )

