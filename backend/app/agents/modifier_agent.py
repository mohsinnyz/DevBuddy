# D:\DevBuddy\backend\app\agents\modifier_agent.py

import os
from typing import List, Dict, Any
from loguru import logger
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage


class ModifierAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

        # ✅ Updated to stable LLaMA 3 model
        self.llm = ChatGroq(
            api_key=api_key,
            model="llama3-8b-8192",
            temperature=0.1
        )

    async def modify(self, instruction: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Modify code, generate documentation, or provide suggestions
        depending strictly on the user instruction.
        """
        try:
            # Build context from chunks
            context_parts = []
            for chunk in context_chunks:
                part = "\n".join(filter(None, [
                    f"File: {chunk.get('file_path', 'Unknown')}",
                    f"Function: {chunk.get('function_name')}" if chunk.get("function_name") else None,
                    f"Class: {chunk.get('class_name')}" if chunk.get("class_name") else None,
                    f"Documentation: {chunk.get('docstring')}" if chunk.get("docstring") else None,
                    f"Code:\n{chunk.get('content', '')}"
                ]))
                context_parts.append(part)

            context_text = "\n\n---\n\n".join(context_parts)

            # System message with tightened role separation
            system_message = SystemMessage(content="""
You are DevBuddy's Code Modifier Agent.

Your role depends strictly on the user instruction:
- If the user asks for performance or improvement suggestions → provide only suggestions.
- If the user asks for code modification or refactoring → provide only modified code.
- If the user asks for documentation or README → provide only documentation.
Do NOT mix tasks unless the user explicitly requests multiple outputs.

General guidelines:
- Always format responses in markdown for readability.
- Use fenced code blocks for code.
- Preserve structure, intent, and readability when modifying code.
- Follow Python best practices.
- When writing documentation, include clear headings and lists.
""")

            # Human message with instruction + context
            human_message = HumanMessage(content=f"""Code Context:
{context_text}

User Instruction:
{instruction}

Respond according to the rules above.
""")

            logger.info(f"Sending modification request to Groq LLaMA 3 for: {instruction[:100]}...")
            response = await self.llm.ainvoke([system_message, human_message])

            return response.content.strip() if hasattr(response, "content") else str(response)

        except Exception as e:
            logger.error(f"Error in ModifierAgent: {e}")
            return f"❌ Error: {str(e)}"

    async def generate_readme(self, context_chunks: List[Dict[str, Any]], repo_url: str) -> str:
        """Generate a README file for the repository"""
        try:
            project_info = self._analyze_project(context_chunks)

            instruction = f"""Generate a comprehensive README.md file.

Project Information:
- Repository: {repo_url}
- Main Language: Python
- Project Type: {project_info.get('project_type', 'Application')}
- Key Features: {', '.join(project_info.get('features', []))}
- Main Files: {', '.join(project_info.get('main_files', []))}

Include:
1. Title & Description
2. Installation Instructions
3. Usage Examples
4. Key Features
5. Requirements
6. Contributing Guidelines
7. License (if applicable)
"""

            return await self.modify(instruction, context_chunks)

        except Exception as e:
            logger.error(f"Error generating README: {e}")
            return f"❌ Error generating README: {str(e)}"

    def _analyze_project(self, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze project structure and features from context chunks"""
        project_info = {
            "project_type": "Application",
            "features": [],
            "main_files": [],
            "has_api": False,
            "has_web_ui": False,
            "has_cli": False
        }

        for chunk in context_chunks:
            file_path = chunk.get("file_path", "")
            content = chunk.get("content", "").lower()

            if any(f in file_path for f in ["main.py", "app.py"]):
                project_info["main_files"].append(file_path)

            if "fastapi" in content or "flask" in content:
                project_info["has_api"] = True
                project_info["features"].append("REST API")

            if "next.js" in content or "react" in content or "<html>" in content:
                project_info["has_web_ui"] = True
                project_info["features"].append("Web UI")

            if "click" in content or "argparse" in content:
                project_info["has_cli"] = True
                project_info["features"].append("CLI")

            if "docker" in content:
                project_info["features"].append("Docker Support")

            if "test" in file_path:
                project_info["features"].append("Testing")

        return project_info
