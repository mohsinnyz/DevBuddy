from typing import List, Dict, Any, Optional
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService
from loguru import logger
import re

class RetrieverAgent:
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant_service = qdrant_service
        self.embedding_service = EmbeddingService()

    async def retrieve(self, query: str, repo_url: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            # Extract keywords for hybrid search
            keywords = self._extract_keywords(query)
            
            # 1. Semantic search with embeddings
            query_embedding = await self.embedding_service.generate_embedding(query)
            semantic_results = await self.qdrant_service.search_similar(
                query_embedding, 
                limit=limit, 
                repo_url=repo_url
            )
            
            # 2. Keyword search if we have keywords
            keyword_results = []
            if keywords:
                keyword_results = await self.qdrant_service.search_by_keywords(
                    keywords, 
                    limit=limit//2, 
                    repo_url=repo_url
                )
            
            # 3. Combine and deduplicate results
            combined_results = self._combine_results(semantic_results, keyword_results, limit)
            
            logger.info(f"RetrieverAgent found {len(combined_results)} results for repo {repo_url}")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error in RetrieverAgent: {e}")
            return []

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from the query"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall'}
        
        # Extract words that look like function names, class names, or technical terms
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Limit to top 5 keywords

    def _combine_results(self, semantic_results: List[Dict], keyword_results: List[Dict], limit: int) -> List[Dict]:
        """Combine and deduplicate search results"""
        combined = {}
        
        # Add semantic results with higher weight
        for result in semantic_results:
            chunk_id = result.get('chunk_id', '')
            if chunk_id not in combined:
                combined[chunk_id] = result
                combined[chunk_id]['score'] = result.get('score', 0) * 1.2  # Boost semantic results
        
        # Add keyword results
        for result in keyword_results:
            chunk_id = result.get('chunk_id', '')
            if chunk_id not in combined:
                combined[chunk_id] = result
            else:
                # If already exists, boost the score
                combined[chunk_id]['score'] = max(
                    combined[chunk_id]['score'], 
                    result.get('score', 0)
                )
        
        # Sort by score and return top results
        sorted_results = sorted(combined.values(), key=lambda x: x.get('score', 0), reverse=True)
        return sorted_results[:limit]
