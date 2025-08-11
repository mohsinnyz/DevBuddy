# D:\DevBuddy\backend\app\agents\retriever_agent.py

from typing import List, Dict, Any, Optional
import logging
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService  # assuming you have this

logger = logging.getLogger(__name__)

class RetrieverAgent:
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant_service = qdrant_service
        self.embedding_service = EmbeddingService()

    async def retrieve(
        self, query: str, repo_url: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        try:
            keywords = self._extract_keywords(query)
            query_embedding = await self.embedding_service.generate_embedding(query)

            semantic_results = await self.qdrant_service.search_similar(
                query_vector=query_embedding,
                limit=limit,
                repo_url=repo_url
            )

            keyword_results = []
            if keywords:
                keyword_results = await self.qdrant_service.search_by_keywords(
                    keywords=keywords,
                    limit=limit // 2,
                    repo_url=repo_url
                )

            combined_results = self._combine_results(semantic_results, keyword_results, limit)
            logger.info(f"RetrieverAgent found {len(combined_results)} results for repo {repo_url}")
            return combined_results

        except Exception as e:
            logger.error(f"Error in RetrieverAgent: {e}", exc_info=True)
            return []

    def _extract_keywords(self, text: str) -> List[str]:
        # Simple placeholder for keyword extraction
        return [w for w in text.split() if len(w) > 3]

    def _combine_results(
        self, semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        seen = set()
        combined = []
        for r in semantic_results + keyword_results:
            if r["chunk_id"] not in seen:
                combined.append(r)
                seen.add(r["chunk_id"])
            if len(combined) >= limit:
                break
        return combined
