"""
Secure Python code compiler/executor using Docker containers
"""

import tempfile
import os
from typing import Dict, Any
import asyncio
import uuid
import shutil

from .config import (
    DOCKER_IMAGE, 
    TIMEOUT, 
    MEMORY_LIMIT, 
    CPU_LIMIT, 
    MAX_OUTPUT_SIZE, 
    TEMP_DIR_SIZE
)


class PythonCompiler:
    """A secure Python code compiler/executor using Docker containers"""
    
    def __init__(self):
        self.timeout = TIMEOUT
        self.docker_image = DOCKER_IMAGE
        self.memory_limit = MEMORY_LIMIT
        self.cpu_limit = CPU_LIMIT
        self.max_output_size = MAX_OUTPUT_SIZE
    
    async def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely in a Docker container
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict containing success status, output, and any errors
        """
        if not code.strip():
            return {
                "success": False,
                "output": "",
                "error": "No code provided"
            }
        
        # Generate a unique container name
        container_name = f"python_exec_{uuid.uuid4().hex[:8]}"
        
        # Create a temporary directory for the code
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "user_code.py")
        
        try:
            # Write the user code to a temporary file
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(code)
            
            # Build Docker command with security restrictions
            docker_cmd = self._build_docker_command(container_name, temp_file_path)
            
            # Execute the Docker container
            result = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=self.max_output_size
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(), 
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                # Kill the container if it times out
                await self._kill_container(container_name)
                return {
                    "success": False,
                    "output": "",
                    "error": f"Code execution timed out after {self.timeout} seconds"
                }
            
            # Process the output
            return self._process_execution_result(result.returncode, stdout, stderr)
                
        except Exception as e:
            # Ensure container is cleaned up in case of exception
            await self._kill_container(container_name)
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}"
            }
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _build_docker_command(self, container_name: str, temp_file_path: str) -> list:
        """Build the Docker run command with security restrictions"""
        return [
            "docker", "run",
            "--rm",  # Remove container after execution
            "--name", container_name,
            "--memory", self.memory_limit,
            "--cpus", self.cpu_limit,
            "--network", "none",  # No network access
            "--read-only",  # Read-only filesystem
            "--tmpfs", f"/tmp:noexec,nosuid,size={TEMP_DIR_SIZE}",  # Limited tmp directory
            "--user", "nobody:nogroup",  # Run as non-root user
            "--security-opt", "no-new-privileges:true",  # Prevent privilege escalation
            "--cap-drop", "ALL",  # Drop all capabilities
            "-v", f"{temp_file_path}:/app/user_code.py:ro",  # Mount code as read-only
            "-w", "/app",  # Set working directory
            self.docker_image,
            "python", "user_code.py"
        ]
    
    def _process_execution_result(self, return_code: int, stdout: bytes, stderr: bytes) -> Dict[str, Any]:
        """Process the execution result and return formatted response"""
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        
        if return_code == 0:
            return {
                "success": True,
                "output": stdout_text,
                "error": ""
            }
        else:
            return {
                "success": False,
                "output": stdout_text,
                "error": stderr_text
            }
    
    async def _kill_container(self, container_name: str):
        """Kill a Docker container if it's still running"""
        try:
            await asyncio.create_subprocess_exec(
                "docker", "kill", container_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
        except Exception:
            pass  # Container might already be stopped
