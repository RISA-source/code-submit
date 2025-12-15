import subprocess
import time
import os
import sys
import shlex
import threading
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
        return [sys_python_executable(), '-u', file_path] # -u for unbuffered
    elif language == 'Java':
        return ['java', file_path]
    else:
        return []

def sys_python_executable():
    import sys
    return sys.executable

def stream_reader(pipe, out_buffer, stream_dest):
    """
    Reads from 'pipe' line by line (or chunk).
    Writes to 'out_buffer' (list of str).
    Writes to 'stream_dest' (e.g. sys.stdout).
    """
    try:
        # iter(pipe.readline, b'') works if pipe is binary
        # If text mode, just pipe.readline
        for line in iter(pipe.readline, ''):
            out_buffer.append(line)
            stream_dest.write(line)
            stream_dest.flush()
    except (ValueError, OSError):
        pass

def execute_files(files: List[SourceFile], config) -> List[Tuple[SourceFile, Optional[ExecutionResult]]]:
    results = []
    
    if not config.execution_enabled:
        return [(f, None) for f in files]

    timeout = config.timeout

    for file in files:
        cmd = get_runner_command(file.path, file.language)
        
        if not cmd:
            print(f"Skipping execution for {file.rel_path} ({file.language}): No runner defined.")
            results.append((file, None))
            continue

        print(f"\n--- Executing {file.rel_path} ---")
        start_time = time.time()
        
        context = {
            "cwd": os.getcwd(),
            "env_user": os.environ.get("USERNAME", "unknown"),
            "env_os": os.name
        }

        timed_out = False
        captured_stdout = []
        captured_stderr = []
        exit_code = 0
        
        try:
            if config.interactive:
                # INTERACTIVE MODE: Full Session Capture
                # We need to capture what the user types AND what the program outputs.
                # Previous attempt (stdin=sys.stdin) bypassed capture.
                # New plan:
                # 1. Thread 1: Read process stdout -> Print to Console + Append to Log
                # 2. Thread 2: Read process stderr -> Print to Console + Append to Log
                # 3. Thread 3 (Main): Read Console stdin -> Write to Process stdin + Append to Log
                
                # Note: Reading sys.stdin on Windows can be blocking.
                # However, since we are in "Interactive Mode", blocking on user input is EXPECTED behavior.
                # We essentially act as a proxy.
                
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE, # We will write to this
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1, # Line buffered
                    errors='replace'
                )
                
                # Shared log for chronological order (optional, but nice)
                # For now, we append input to captured_stdout to make it look like a terminal session.
                
                # Actually, 'msvcrt' is low level console.
                # Simpler: Just run a thread that reads input() and writes line-by-line?
                # Does that show characters as they are typed? Yes, the terminal handles echo.
                
                def input_thread_func():
                    try:
                        while proc.poll() is None:
                            # Use input() to block wait for line?
                            # If we block, we can't exit when proc dies?
                            # Thread will die when daemonized?
                            line = sys.stdin.readline()
                            if not line: break
                            
                            try:
                                proc.stdin.write(line)
                                proc.stdin.flush()
                                captured_stdout.append(line) # Add USER INPUT to the captured log
                            except IOError:
                                break
                    except:
                        pass

                t_in = threading.Thread(target=input_thread_func)
                t_in.daemon = True # Die when main dies
                t_in.start()

                t_out = threading.Thread(target=stream_reader, args=(proc.stdout, captured_stdout, sys.stdout))
                t_err = threading.Thread(target=stream_reader, args=(proc.stderr, captured_stderr, sys.stderr))
                
                t_out.start()
                t_err.start()
                
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    timed_out = True
                
                t_out.join(timeout=1)
                t_err.join(timeout=1)
                # t_in might still be blocked on readline, but daemon=True handles it.
                
                exit_code = proc.returncode

            else:
                # BATCH MODE
                stdin_content = config.stdin_input.encode('utf-8') if config.stdin_input else b""
                proc = subprocess.run(
                    cmd,
                    input=stdin_content,
                    capture_output=True,
                    timeout=timeout,
                    check=False
                )
                captured_stdout = [proc.stdout.decode('utf-8', errors='replace')]
                captured_stderr = [proc.stderr.decode('utf-8', errors='replace')]
                exit_code = proc.returncode
            
            duration = time.time() - start_time
            
            res = ExecutionResult(
                stdout="".join(captured_stdout),
                stderr="".join(captured_stderr),
                exit_code=exit_code if exit_code is not None else -1,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=timed_out
            )
            
        except Exception as e:
            duration = time.time() - start_time
            res = ExecutionResult(
                stdout="".join(captured_stdout),
                stderr=str(e),
                exit_code=-1,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=False
            )
            
        results.append((file, res))
        
    return results
