from dataclasses import dataclass, field
from typing import List, Optional, Dict
import yaml
import os

@dataclass
class Config:
    project_title: str = "Assignment"
    author: str = "Student"
    input_root: str = "."
    extensions: List[str] = field(default_factory=lambda: [".py", ".java"])
    input_file: Optional[str] = None
    execution_enabled: bool = True
    timeout: int = 5
    stdin_input: str = ""
    interactive: bool = False

def load_config(path: str) -> Config:
    if not os.path.exists(path):
        return Config() # Default
    
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    
    # Parse inputs (Stub logic)
    proj = data.get("project", {})
    inp = data.get("input", {})
    exe = data.get("execution", {})
    
    return Config(
        project_title=proj.get("title", "Assignment"),
        author=proj.get("author", "Student"),
        input_root=inp.get("root", "."),
        extensions=inp.get("extensions", [".py", ".java"]),
        input_file=inp.get("input_file"),
        execution_enabled=exe.get("enabled", True),
        timeout=exe.get("timeout", 5),
        stdin_input=exe.get("stdin_input", ""),
        interactive=exe.get("interactive", data.get("interactive", False))
    )
