from fastapi import APIRouter, Request
from app.models.schemas import HealthResponse
from datetime import datetime

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health(request: Request):
    qdrant_service = request.app.state.qdrant_service
    info = await qdrant_service.get_collection_info()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        services={"qdrant": str(info)},
        timestamp=datetime.utcnow().isoformat()
    )
