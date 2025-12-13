import hashlib
import os
from dataclasses import dataclass
from typing import List, Set

@dataclass
class SourceFile:
    path: str       # Absolute path
    rel_path: str   # Relative to input root
    language: str   # Derived from extension
    hash_digest: str
    content: str    # Read content purely for formatting (or lazy load?) - let's read it now for simplicity

def calculate_hash(path: str) -> str:
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def detect_language(ext: str) -> str:
    mapping = {
        '.py': 'Python',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.go': 'Go',
        '.rs': 'Rust'
    }
    return mapping.get(ext, 'Unknown')

def scan_directory(config) -> List[SourceFile]:
    root_path = os.path.abspath(config.input_root)
    extensions: Set[str] = set(config.extensions)
    results = []

    if not os.path.exists(root_path):
        raise FileNotFoundError(f"Input root not found: {root_path}")

    for root, dirs, files in os.walk(root_path):
        # Exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in extensions:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_path)
                
                # Check exclusion patterns if any (TODO)
                
                try:
                    file_hash = calculate_hash(full_path)
                    # Read content gently (utf-8 assumed for source code)
                    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                        
                    results.append(SourceFile(
                        path=full_path,
                        rel_path=rel_path,
                        language=detect_language(ext),
                        hash_digest=file_hash,
                        content=content
                    ))
                except Exception as e:
                    # Skip problematic files but maybe log warning?
                    print(f"Warning: Could not read {full_path}: {e}")
                    continue
    
    # Deterministic sorting: by relative path
    results.sort(key=lambda x: x.rel_path)
    return results

