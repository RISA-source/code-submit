import subprocess
import time
import os
import shlex
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Optional
from .scanner import SourceFile

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    command: str
    context: Dict[str, str]
    timed_out: bool

    def to_dict(self):
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration": self.duration,
            "command": self.command,
            "context": self.context,
            "timed_out": self.timed_out
        }

def get_runner_command(file_path: str, language: str) -> List[str]:
    """Returns the command list to execute the file based on language."""
    if language == 'Python':
        return [sys_python_executable(), file_path]
    elif language == 'Java':
        # Java 11+ single file source code execution
        return ['java', file_path]
    else:
        return []

def sys_python_executable():
    import sys
    return sys.executable

def execute_files(files: List[SourceFile], config) -> List[Tuple[SourceFile, Optional[ExecutionResult]]]:
    results = []
    
    if not config.execution_enabled:
        return [(f, None) for f in files]

    # Prepare input
    stdin_content = config.stdin_input.encode('utf-8') if config.stdin_input else b""
    # Only load file input if explicitly set and strictly required (ignoring complex logic for now)
    if config.input_file and os.path.exists(config.input_file):
        with open(config.input_file, 'rb') as f:
            stdin_content = f.read()

    timeout = config.timeout

    for file in files:
        cmd = get_runner_command(file.path, file.language)
        
        if not cmd:
            # No runner for this language
            print(f"Skipping execution for {file.rel_path} ({file.language}): No runner defined.")
            results.append((file, None))
            continue

        print(f"Executing {file.rel_path}...")
        start_time = time.time()
        
        context = {
            "cwd": os.getcwd(),
            # Capture a safe subset of env vars or all? User requested environment freeze.
            # Capturing everything might be noisy, let's capture important ones.
            "env_user": os.environ.get("USERNAME", "unknown"),
            "env_os": os.name
        }

        try:
            # Using subprocess.run for simplicity
            proc = subprocess.run(
                cmd,
                input=stdin_content,
                capture_output=True,
                timeout=timeout,
                check=False # Don't raise on non-zero exit
            )
            
            duration = time.time() - start_time
            
            res = ExecutionResult(
                stdout=proc.stdout.decode('utf-8', errors='replace'),
                stderr=proc.stderr.decode('utf-8', errors='replace'),
                exit_code=proc.returncode,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=False
            )
            
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            res = ExecutionResult(
                stdout=e.stdout.decode('utf-8', errors='replace') if e.stdout else "",
                stderr=e.stderr.decode('utf-8', errors='replace') if e.stderr else "Timeout Expired",
                exit_code=-1,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=True
            )
        except Exception as e:
            duration = time.time() - start_time
            res = ExecutionResult(
                stdout="",
                stderr=f"Execution Failed: {str(e)}",
                exit_code=-1,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=False
            )
            
        results.append((file, res))
        
    return results

