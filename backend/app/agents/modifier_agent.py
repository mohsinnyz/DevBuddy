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

        # ✅ Updated model from deprecated Mixtral to LLaMA 3
        self.llm = ChatGroq(
            api_key=api_key,
            model="llama3-8b-8192",  # new stable Groq model
            temperature=0.1
        )

    async def modify(self, instruction: str, context_chunks: List[Dict[str, Any]]) -> str:
        try:
            # Build context from chunks
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

            # System message
            system_message = SystemMessage(content="""
You are DevBuddy's Code Modifier Agent.
Your role is to:
1. Modify code based on user instructions
2. Create README files and documentation
3. Suggest improvements & refactoring
4. Generate patches/snippets
5. Follow code style and best practices
                                           
 Your output should always be formatted using markdown to improve readability. Use code blocks for code snippets, headings for sections, and bolding or italics for emphasis.


When modifying code:
- Preserve structure and intent
- Add meaningful comments
- Ensure functionality and readability
- Follow Python best practices

When creating README:
- Include installation, usage, features, examples
- Follow standard formatting
""")

            # Human message
            human_message = HumanMessage(content=f"""Code Context:
{context_text}

User Instruction:
{instruction}

Provide the modified code, README, or documentation as per the instruction.
Ensure completeness and clarity.
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
        """Analyze project structure and features"""
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
