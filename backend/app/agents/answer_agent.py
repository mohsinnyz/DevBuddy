import os
from typing import List, Dict, Any
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

class AnswerAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        self.llm = ChatGoogleGenerativeAI(
            api_key=api_key, 
            model="gemini-1.5-flash-latest",
            temperature=0.1
        )

    async def answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        try:
            # Compose context with better formatting
            context_parts = []
            for chunk in context_chunks:
                context_part = f"File: {chunk.get('file_path', 'Unknown')}"
                if chunk.get('function_name'):
                    context_part += f"\nFunction: {chunk['function_name']}"
                if chunk.get('class_name'):
                    context_part += f"\nClass: {chunk['class_name']}"
                if chunk.get('docstring'):
                    context_part += f"\nDocumentation: {chunk['docstring']}"
                context_part += f"\nCode:\n{chunk.get('content', '')}"
                context_parts.append(context_part)
            
            context_text = "\n\n---\n\n".join(context_parts)
            
            # Create system message
            system_message = SystemMessage(content="""You are DevBuddy, an intelligent codebase assistant. 
Your role is to help users understand and work with their codebase by:
1. Analyzing the provided code context
2. Explaining functions, classes, and code patterns
3. Providing clear, accurate answers about the codebase
4. Suggesting improvements when appropriate
5. Being concise but thorough in your explanations

Always base your answers on the provided code context. If the context doesn't contain enough information to answer the question, say so clearly.""")
            
            # Create human message
            human_message = HumanMessage(content=f"""Context from the codebase:
{context_text}

User Question: {query}

Please provide a helpful answer based on the code context above.""")
            
            logger.info(f"Sending query to Gemini Answer Agent: {query[:100]}...")
            response = await self.llm.ainvoke([system_message, human_message])
            
            return response.content.strip() if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Error in AnswerAgent: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
