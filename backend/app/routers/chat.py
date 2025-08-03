from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatRequest, ChatResponse
from app.agents.retriever_agent import RetrieverAgent
from app.agents.answer_agent import AnswerAgent
from app.agents.modifier_agent import ModifierAgent
from loguru import logger
import time
import re

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest):
    qdrant_service = request.app.state.qdrant_service
    retriever = RetrieverAgent(qdrant_service)
    answer_agent = AnswerAgent()
    modifier_agent = ModifierAgent()
    start = time.time()
    
    try:
        # Determine which agent to use based on the query
        agent_used, response, context = await _process_chat_message(
            payload, retriever, answer_agent, modifier_agent
        )
        
        elapsed = time.time() - start
        return ChatResponse(
            response=response,
            sources=context,
            agent_used=agent_used,
            processing_time=elapsed
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

async def _process_chat_message(payload: ChatRequest, retriever, answer_agent, modifier_agent):
    """Process chat message and determine appropriate agent"""
    message = payload.message.strip().lower()
    
    # Check for specific commands
    if _is_modification_request(message):
        context = await retriever.retrieve(
            payload.message, 
            repo_url=payload.repo_url, 
            limit=payload.max_context_chunks
        )
        response = await modifier_agent.modify(payload.message, context)
        return "modifier", response, context
    
    elif _is_readme_request(message):
        context = await retriever.retrieve(
            payload.message, 
            repo_url=payload.repo_url, 
            limit=payload.max_context_chunks
        )
        response = await modifier_agent.generate_readme(context, payload.repo_url or "")
        return "modifier", response, context
    
    else:
        # Default: answer agent for general questions
        context = await retriever.retrieve(
            payload.message, 
            repo_url=payload.repo_url, 
            limit=payload.max_context_chunks
        )
        response = await answer_agent.answer(payload.message, context)
        return "answer", response, context

def _is_modification_request(message: str) -> bool:
    """Check if the message is a modification request"""
    modification_keywords = [
        'modify', 'change', 'update', 'edit', 'refactor', 'improve',
        'add', 'create', 'generate', 'write', 'implement'
    ]
    return any(keyword in message for keyword in modification_keywords)

def _is_readme_request(message: str) -> bool:
    """Check if the message is a README generation request"""
    readme_keywords = ['readme', 'documentation', 'docs', 'document']
    return any(keyword in message for keyword in readme_keywords)
