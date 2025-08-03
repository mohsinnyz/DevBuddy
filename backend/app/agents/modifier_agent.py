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
        self.llm = ChatGroq(
            api_key=api_key, 
            model="mixtral-8x7b-32768",
            temperature=0.1
        )

    async def modify(self, instruction: str, context_chunks: List[Dict[str, Any]]) -> str:
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
            system_message = SystemMessage(content="""You are DevBuddy's Code Modifier Agent, powered by Groq Mixtral.
Your role is to:
1. Generate code modifications based on user instructions
2. Create README files and documentation
3. Suggest code improvements and refactoring
4. Generate patches and code snippets
5. Maintain code style and best practices

When modifying code:
- Preserve the original structure and intent
- Add appropriate comments and documentation
- Follow Python best practices
- Ensure the code is functional and readable

When creating README files:
- Include clear installation instructions
- Document key features and usage
- Add examples where appropriate
- Follow standard README conventions""")
            
            # Create human message
            human_message = HumanMessage(content=f"""Code Context:
{context_text}

User Instruction: {instruction}

Please provide the modified code, README, or implementation based on the instruction above. 
If generating code, ensure it's complete and functional. If creating documentation, make it comprehensive and clear.""")
            
            logger.info(f"Sending modification request to Groq Modifier Agent: {instruction[:100]}...")
            response = await self.llm.ainvoke([system_message, human_message])
            
            return response.content.strip() if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Error in ModifierAgent: {e}")
            return f"I apologize, but I encountered an error while processing your modification request: {str(e)}"

    async def generate_readme(self, context_chunks: List[Dict[str, Any]], repo_url: str) -> str:
        """Generate a README file for the repository"""
        try:
            # Analyze the codebase to understand the project
            project_info = self._analyze_project(context_chunks)
            
            instruction = f"""Generate a comprehensive README.md file for this project.
            
Project Information:
- Repository: {repo_url}
- Main Language: Python
- Project Type: {project_info.get('project_type', 'Application')}
- Key Features: {', '.join(project_info.get('features', []))}
- Main Files: {', '.join(project_info.get('main_files', []))}

Please create a professional README with:
1. Project title and description
2. Installation instructions
3. Usage examples
4. Key features
5. Requirements/dependencies
6. Contributing guidelines
7. License information (if applicable)"""
            
            return await self.modify(instruction, context_chunks)
            
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            return f"Error generating README: {str(e)}"

    def _analyze_project(self, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the project structure to understand the codebase"""
        project_info = {
            'project_type': 'Application',
            'features': [],
            'main_files': [],
            'has_api': False,
            'has_web_ui': False,
            'has_cli': False
        }
        
        # Analyze chunks to understand project structure
        for chunk in context_chunks:
            file_path = chunk.get('file_path', '')
            content = chunk.get('content', '').lower()
            
            # Detect project type and features
            if 'main.py' in file_path or 'app.py' in file_path:
                project_info['main_files'].append(file_path)
            
            if 'fastapi' in content or 'flask' in content:
                project_info['has_api'] = True
                project_info['features'].append('REST API')
            
            if 'next.js' in content or 'react' in content or 'html' in content:
                project_info['has_web_ui'] = True
                project_info['features'].append('Web UI')
            
            if 'click' in content or 'argparse' in content:
                project_info['has_cli'] = True
                project_info['features'].append('CLI')
            
            if 'docker' in content:
                project_info['features'].append('Docker Support')
            
            if 'test' in file_path:
                project_info['features'].append('Testing')
        
        return project_info
