# D:\DevBuddy\backend\app\utils\git_utils.py
import os
import shutil
from typing import Optional, List
from git import Repo, GitCommandError
from loguru import logger
from urllib.parse import urlparse


class GitUtils:
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or os.getenv("TEMP_REPO_DIR", "/tmp/repos")
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"[GitUtils] Temporary repo directory: {self.temp_dir}")

    def extract_repo_info(self, repo_url: str):
        """Extracts owner and repo name from the GitHub repo URL."""
        try:
            repo_url_str = str(repo_url)  # ✅ Ensure string type
            parsed_url = urlparse(repo_url_str)
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) < 2:
                raise ValueError("URL does not contain valid owner/repo info")
            owner, name = path_parts[0], path_parts[1].replace('.git', '')
            return {"owner": owner, "name": name, "full_name": f"{owner}/{name}"}
        except Exception as e:
            logger.error(f"Failed to parse repo URL {repo_url}: {e}")
            raise

    def get_repo_local_path(self, repo_url: str) -> str:
        """Returns the local path to store the cloned repository."""
        repo_url = str(repo_url)  # ✅ Ensure string type

        # ✅ If already a local path, return it directly
        if os.path.exists(repo_url):
            return repo_url

        repo_info = self.extract_repo_info(repo_url)
        return os.path.join(self.temp_dir, f"{repo_info['owner']}_{repo_info['name']}")

    async def clone_repository(self, repo_url: str, branch: str = "main", force: bool = False) -> str:
        """Clones the GitHub repository into a local path."""
        try:
            repo_url = str(repo_url)  # ✅ Ensure string type

            # ✅ If already a local path, skip cloning
            if os.path.exists(repo_url):
                logger.info(f"Repository path detected locally at {repo_url}, skipping clone.")
                return repo_url

            local_path = self.get_repo_local_path(repo_url)

            if force and os.path.exists(local_path):
                shutil.rmtree(local_path)
                logger.info(f"Removed existing repository at {local_path}")

            if os.path.exists(local_path):
                logger.info(f"Repository already exists at {local_path}")
                return local_path

            logger.info(f"Cloning repository {repo_url} to {local_path}")

            branches_to_try = [branch] + [b for b in ["main", "master"] if b != branch]
            repo = None

            for branch_name in branches_to_try:
                try:
                    repo = Repo.clone_from(repo_url, local_path, branch=branch_name, depth=1)
                    logger.info(f"Successfully cloned repository on branch: {branch_name}")
                    break
                except GitCommandError as e:
                    if "Remote branch" in str(e) and "not found" in str(e):
                        logger.warning(f"Branch '{branch_name}' not found, trying next...")
                        continue
                    else:
                        logger.error(f"Git clone error: {e}")
                        raise

            if repo is None:
                raise GitCommandError(f"Failed to clone repository using any branch: {branches_to_try}")

            return local_path

        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            raise

    async def get_python_files(self, repo_url: str, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """Clones repo (if not exists) and returns list of Python files."""
        try:
            repo_url = str(repo_url)  # ✅ Ensure string type
            repo_path = await self.clone_repository(repo_url)

            include_patterns = include_patterns or ["*.py"]
            exclude_dirs = {".git", "venv", "env", "__pycache__", ".venv"}
            exclude_files = {".pyc", ".pyo"}

            python_files = []

            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in files:
                    if file.endswith(".py") and not any(file.endswith(ext) for ext in exclude_files):
                        python_files.append(os.path.join(root, file))

            logger.info(f"Found {len(python_files)} Python files in {repo_path}")
            return python_files

        except Exception as e:
            logger.error(f"Failed to get Python files from {repo_url}: {e}")
            raise

    def cleanup_repository(self, repo_url: str):
        """Deletes the locally cloned repository to free up space."""
        try:
            repo_url = str(repo_url)  # ✅ Ensure string type
            local_path = self.get_repo_local_path(repo_url)
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                logger.info(f"Cleaned up repository at {local_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup repository {repo_url}: {e}")

    def get_file_content(self, file_path: str) -> str:
        """Reads file content with fallback for encoding errors."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                return ""
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""
