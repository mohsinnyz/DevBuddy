import os
import shutil
import tempfile
from typing import Optional, List
from git import Repo, GitCommandError
from loguru import logger
from urllib.parse import urlparse

class GitUtils:
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or os.getenv("TEMP_REPO_DIR", "/tmp/repos")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_repo_info(self, repo_url: str) -> dict:
        """Extract repository information from URL"""
        try:
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo_name = path_parts[1].replace('.git', '')
                
                return {
                    "owner": owner,
                    "repo_name": repo_name,
                    "full_name": f"{owner}/{repo_name}",
                    "host": parsed.netloc
                }
            else:
                raise ValueError("Invalid repository URL format")
                
        except Exception as e:
            logger.error(f"Failed to parse repo URL {repo_url}: {e}")
            raise
    
    def get_repo_local_path(self, repo_url: str) -> str:
        """Get local path for cloned repository"""
        repo_info = self.extract_repo_info(repo_url)
        return os.path.join(self.temp_dir, repo_info["full_name"])
    
    async def clone_repository(self, repo_url: str, branch: str = "main", force: bool = False) -> str:
        """Clone a repository to local storage"""
        try:
            local_path = self.get_repo_local_path(repo_url)
            
            # Remove existing directory if force is True
            if force and os.path.exists(local_path):
                shutil.rmtree(local_path)
                logger.info(f"Removed existing repository at {local_path}")
            
            # Check if repository already exists
            if os.path.exists(local_path):
                logger.info(f"Repository already exists at {local_path}")
                return local_path
            
            # Clone the repository
            logger.info(f"Cloning repository {repo_url} to {local_path}")
            
            # Try main branch first, then master if main fails
            branches_to_try = [branch, "main", "master"] if branch != "main" else ["main", "master"]
            
            repo = None
            for branch_name in branches_to_try:
                try:
                    repo = Repo.clone_from(
                        repo_url,
                        local_path,
                        branch=branch_name,
                        depth=1  # Shallow clone for faster cloning
                    )
                    logger.info(f"Successfully cloned repository on branch: {branch_name}")
                    break
                except GitCommandError as e:
                    if "Remote branch" in str(e) and "not found" in str(e):
                        logger.warning(f"Branch {branch_name} not found, trying next...")
                        continue
                    else:
                        raise
            
            if repo is None:
                raise GitCommandError("Failed to clone repository with any available branch")
            
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            raise
    
    def get_python_files(self, repo_path: str, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """Get list of Python files in repository"""
        try:
            if include_patterns is None:
                include_patterns = ["*.py"]
            
            if exclude_patterns is None:
                exclude_patterns = ["__pycache__", "*.pyc", ".git", "venv", "env", ".env"]
            
            python_files = []
            
            for root, dirs, files in os.walk(repo_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                
                for file in files:
                    if file.endswith('.py'):
                        # Check if file matches exclude patterns
                        if any(pattern in file or pattern in root for pattern in exclude_patterns):
                            continue
                        
                        file_path = os.path.join(root, file)
                        python_files.append(file_path)
            
            logger.info(f"Found {len(python_files)} Python files in {repo_path}")
            return python_files
            
        except Exception as e:
            logger.error(f"Failed to get Python files from {repo_path}: {e}")
            raise
    
    def cleanup_repository(self, repo_url: str):
        """Clean up cloned repository"""
        try:
            local_path = self.get_repo_local_path(repo_url)
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                logger.info(f"Cleaned up repository at {local_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup repository {repo_url}: {e}")
    
    def get_file_content(self, file_path: str) -> str:
        """Read content of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                return ""
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""
