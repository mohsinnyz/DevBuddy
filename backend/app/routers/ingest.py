from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import IngestionRequest, IngestionResponse
from app.agents.ingestion_agent import IngestionAgent
from loguru import logger
from uuid import uuid4

router = APIRouter()

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_repo(request: Request, payload: IngestionRequest):
    qdrant_service = request.app.state.qdrant_service
    agent = IngestionAgent(qdrant_service)
    task_id = str(uuid4())
    try:
        result = await agent.ingest_repo(
            repo_url=payload.repo_url,
            branch=payload.branch,
            include_patterns=payload.include_patterns,
            exclude_patterns=payload.exclude_patterns
        )
        return IngestionResponse(
            task_id=task_id,
            status="completed",
            message=f"Ingestion completed for {payload.repo_url}",
            repo_url=payload.repo_url
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
