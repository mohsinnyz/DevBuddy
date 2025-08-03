import ast
from typing import List, Dict, Any, Optional
from loguru import logger

class ASTChunker:
    """Chunk Python code into functions, classes, and modules using AST."""
    def __init__(self):
        pass

    def chunk_code(self, file_path: str, code: str) -> List[Dict[str, Any]]:
        """Chunk code into functions, classes, and module-level code."""
        try:
            tree = ast.parse(code)
            chunks = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    chunks.append(self._extract_chunk(node, code, file_path, 'class'))
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef):
                            chunks.append(self._extract_chunk(subnode, code, file_path, 'function', class_name=node.name))
                elif isinstance(node, ast.FunctionDef):
                    chunks.append(self._extract_chunk(node, code, file_path, 'function'))
            # Module-level code
            module_chunk = self._extract_module_chunk(tree, code, file_path)
            if module_chunk:
                chunks.append(module_chunk)
            return chunks
        except Exception as e:
            logger.error(f"Failed to chunk code for {file_path}: {e}")
            return []

    def _extract_chunk(self, node, code, file_path, chunk_type, class_name=None):
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', None)
        if not end_line:
            # Fallback if end_lineno is not available
            end_line = self._infer_end_line(node)
        lines = code.splitlines()[start_line-1:end_line]
        docstring = ast.get_docstring(node)
        return {
            'chunk_id': f"{file_path}:{start_line}-{end_line}",
            'file_path': file_path,
            'function_name': getattr(node, 'name', None) if chunk_type == 'function' else None,
            'class_name': class_name if class_name else (getattr(node, 'name', None) if chunk_type == 'class' else None),
            'start_line': start_line,
            'end_line': end_line,
            'content': '\n'.join(lines),
            'chunk_type': chunk_type,
            'docstring': docstring
        }

    def _extract_module_chunk(self, tree, code, file_path):
        # Module-level code (outside any class/function)
        # For simplicity, just include the whole file minus functions/classes
        # (Could be improved for more granularity)
        try:
            lines = code.splitlines()
            return {
                'chunk_id': f"{file_path}:module",
                'file_path': file_path,
                'function_name': None,
                'class_name': None,
                'start_line': 1,
                'end_line': len(lines),
                'content': '\n'.join(lines),
                'chunk_type': 'module',
                'docstring': ast.get_docstring(tree)
            }
        except Exception as e:
            logger.error(f"Failed to extract module chunk for {file_path}: {e}")
            return None

    def _infer_end_line(self, node):
        # Fallback for Python <3.8
        max_lineno = node.lineno
        for child in ast.walk(node):
            if hasattr(child, 'lineno'):
                max_lineno = max(max_lineno, child.lineno)
        return max_lineno
