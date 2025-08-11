import os
from typing import List, Dict, Any
from loguru import logger
from app.utils.git_utils import GitUtils
from app.utils.ast_utils import ASTChunker
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

class IngestionAgent:
    def __init__(self, qdrant_service: QdrantService):
        self.git_utils = GitUtils()
        self.ast_chunker = ASTChunker()
        self.embedding_service = EmbeddingService()
        self.qdrant_service = qdrant_service

    async def ingest_repo(
        self,
        repo_url: str,
        branch: str = "main",
        include_patterns=None,
        exclude_patterns=None
    ) -> Dict[str, Any]:
        logger.info(f"Ingestion started for {repo_url}")
        
        # 1. Clone repo
        repo_path = await self.git_utils.clone_repository(
            str(repo_url),  # ensure it's a string
            branch=branch,
            force=True
        )

        # 2. Find Python files
        py_files = await self.git_utils.get_python_files(
            repo_path,
            include_patterns,
            exclude_patterns
        )

        all_chunks = []
        for file_path in py_files:
            code = self.git_utils.get_file_content(file_path)
            chunks = self.ast_chunker.chunk_code(file_path, code)
            for chunk in chunks:
                chunk['repo_url'] = str(repo_url)  # store as string
                chunk['file_extension'] = '.py'
            all_chunks.extend(chunks)

        # 3. Generate embeddings
        embeddings = self.embedding_service.embed_code_chunks(all_chunks)

        # 4. Store in Qdrant
        self.qdrant_service.store_chunks(embeddings, all_chunks)

        logger.info(f"Ingestion completed for {repo_url}")
        return {
            "repo_url": str(repo_url),  # ✅ valid dict key-value
            "files_processed": len(py_files),
            "chunks_created": len(all_chunks)
        }
