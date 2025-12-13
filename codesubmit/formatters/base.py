from abc import ABC, abstractmethod
from typing import List, Tuple
# from ..executor import ExecutionResult
# from ..scanner import SourceFile

class BaseFormatter(ABC):
    @abstractmethod
    def format(self, results: List[Tuple['SourceFile', 'ExecutionResult']], config) -> str:
        """Return content as string. Implemented by text-based formatters."""
        pass
        
    def save(self, results: List[Tuple['SourceFile', 'ExecutionResult']], config, output_path: str):
        """Save content to file. Can be overridden for binary formats like DOCX."""
        content = self.format(results, config)
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(content)
