"""
Comprehensive test suite for the Online Python Compiler backend
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from .app import create_app
from .compiler import PythonCompiler
from .llm_analyzer import LLMCodeAnalyzer


class TestPythonCompiler:
    """Test cases for the PythonCompiler class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.compiler = PythonCompiler()
    
    @pytest.mark.asyncio
    async def test_execute_simple_code(self):
        """Test execution of simple Python code"""
        code = "print('Hello, World!')"
        result = await self.compiler.execute_code(code)
        
        assert result["success"] is True
        assert "Hello, World!" in result["output"]
        assert result["error"] == ""
    
    @pytest.mark.asyncio
    async def test_execute_empty_code(self):
        """Test execution with empty code"""
        result = await self.compiler.execute_code("")
        
        assert result["success"] is False
        assert result["error"] == "No code provided"
    
    @pytest.mark.asyncio
    async def test_execute_code_with_syntax_error(self):
        """Test execution of code with syntax errors"""
        code = "print('Hello World'"  # Missing closing parenthesis
        result = await self.compiler.execute_code(code)
        
        assert result["success"] is False
        assert "SyntaxError" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_code_with_runtime_error(self):
        """Test execution of code with runtime errors"""
        code = "x = 1 / 0"  # Division by zero
        result = await self.compiler.execute_code(code)
        
        assert result["success"] is False
        assert "ZeroDivisionError" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_code_with_variables(self):
        """Test execution of code with variables and calculations"""
        code = """
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""
        result = await self.compiler.execute_code(code)
        
        assert result["success"] is True
        assert "Result: 30" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_code_with_imports(self):
        """Test execution of code with standard library imports"""
        code = """
import math
result = math.sqrt(16)
print(f"Square root of 16: {result}")
"""
        result = await self.compiler.execute_code(code)
        
        assert result["success"] is True
        assert "Square root of 16: 4.0" in result["output"]
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_execute_code_timeout_handling(self, mock_subprocess):
        """Test timeout handling during code execution"""
        # Mock a process that times out
        mock_process = Mock()
        mock_process.communicate.side_effect = asyncio.TimeoutError()
        mock_process.kill = Mock()
        mock_subprocess.return_value = mock_process
        
        code = "while True: pass"  # Infinite loop
        result = await self.compiler.execute_code(code)
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()


class TestLLMCodeAnalyzer:
    """Test cases for the LLMCodeAnalyzer class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.analyzer = LLMCodeAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_empty_code(self):
        """Test analysis of empty code"""
        result = await self.analyzer.analyze_code("")
        
        assert result["success"] is False
        assert result["error"] == "No code provided"
        assert result["is_safe"] is False
    
    @pytest.mark.asyncio
    async def test_analyze_simple_safe_code(self):
        """Test analysis of simple, safe code"""
        code = "print('Hello, World!')"
        
        # Mock the LLM API response
        mock_response = {
            "success": True,
            "security_issues": [],
            "syntax_errors": [],
            "suggestions": ["Good use of print function"],
            "is_safe": True,
            "error": ""
        }
        
        with patch.object(self.analyzer, '_call_llm_api', return_value=mock_response):
            result = await self.analyzer.analyze_code(code)
        
        assert result["success"] is True
        assert result["is_safe"] is True
        assert len(result["security_issues"]) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_code_with_security_issues(self):
        """Test analysis of code with potential security issues"""
        code = "import os; os.system('rm -rf /')"
        
        # Mock the LLM API response with security issues
        mock_response = {
            "success": True,
            "security_issues": [
                {
                    "type": "dangerous_system_call",
                    "severity": "high",
                    "message": "Dangerous system call detected",
                    "line": 1
                }
            ],
            "syntax_errors": [],
            "suggestions": ["Avoid using os.system() with user input"],
            "is_safe": False,
            "error": ""
        }
        
        with patch.object(self.analyzer, '_call_llm_api', return_value=mock_response):
            result = await self.analyzer.analyze_code(code)
        
        assert result["success"] is True
        assert result["is_safe"] is False
        assert len(result["security_issues"]) > 0
        assert result["security_issues"][0]["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_analyze_code_with_syntax_errors(self):
        """Test analysis of code with syntax errors"""
        code = "def func(\nprint('incomplete')"
        
        mock_response = {
            "success": True,
            "security_issues": [],
            "syntax_errors": [
                {
                    "type": "syntax_error",
                    "message": "Invalid syntax",
                    "line": 1
                }
            ],
            "suggestions": ["Fix the function definition syntax"],
            "is_safe": True,
            "error": ""
        }
        
        with patch.object(self.analyzer, '_call_llm_api', return_value=mock_response):
            result = await self.analyzer.analyze_code(code)
        
        assert result["success"] is True
        assert len(result["syntax_errors"]) > 0


class TestRoutes:
    """Test cases for FastAPI routes"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_home_route(self):
        """Test the home page route"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_health_check_route(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "docker_image" in data
        assert "timeout" in data
    
    @patch('backend.routes.compiler.execute_code')
    def test_compile_code_route_success(self, mock_execute):
        """Test successful code compilation via API"""
        # Mock successful execution
        mock_execute.return_value = {
            "success": True,
            "output": "Hello, World!",
            "error": ""
        }
        
        response = self.client.post("/compile", data={"code": "print('Hello, World!')"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Hello, World!" in data["output"]
    
    @patch('backend.routes.compiler.execute_code')
    def test_compile_code_route_error(self, mock_execute):
        """Test code compilation with errors via API"""
        # Mock execution with error
        mock_execute.return_value = {
            "success": False,
            "output": "",
            "error": "SyntaxError: invalid syntax"
        }
        
        response = self.client.post("/compile", data={"code": "print('Hello World'"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "SyntaxError" in data["error"]
    
    @patch('backend.routes.analyzer.analyze_code')
    def test_analyze_code_route(self, mock_analyze):
        """Test code analysis via API"""
        # Mock analysis result
        mock_analyze.return_value = {
            "success": True,
            "security_issues": [],
            "syntax_errors": [],
            "suggestions": ["Good code structure"],
            "is_safe": True,
            "error": ""
        }
        
        response = self.client.post("/analyze", data={"code": "print('Hello, World!')"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["is_safe"] is True
    
    @patch('backend.routes.analyzer.analyze_code')
    @patch('backend.routes.compiler.execute_code')
    def test_analyze_and_compile_safe_code(self, mock_execute, mock_analyze):
        """Test analyze and compile with safe code"""
        # Mock safe analysis
        mock_analyze.return_value = {
            "success": True,
            "security_issues": [],
            "syntax_errors": [],
            "suggestions": [],
            "is_safe": True,
            "error": ""
        }
        
        # Mock successful execution
        mock_execute.return_value = {
            "success": True,
            "output": "Hello, World!",
            "error": ""
        }
        
        response = self.client.post("/analyze-and-compile", data={"code": "print('Hello, World!')"})
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        assert "execution" in data
        assert data["execution"]["success"] is True
    
    @patch('backend.routes.analyzer.analyze_code')
    def test_analyze_and_compile_unsafe_code(self, mock_analyze):
        """Test analyze and compile with unsafe code - should block execution"""
        # Mock unsafe analysis with high severity issue
        mock_analyze.return_value = {
            "success": True,
            "security_issues": [
                {
                    "type": "dangerous_system_call",
                    "severity": "high",
                    "message": "Dangerous operation detected"
                }
            ],
            "syntax_errors": [],
            "suggestions": [],
            "is_safe": False,
            "error": ""
        }
        
        response = self.client.post("/analyze-and-compile", data={"code": "import os; os.system('rm -rf /')"})
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        assert "execution" in data
        assert data["execution"]["success"] is False
        assert "security concerns" in data["execution"]["error"]


class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_complete_workflow_safe_code(self):
        """Test the complete workflow with safe code"""
        safe_code = """
# Calculate factorial
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5 is: {result}")
"""
        
        # First test analysis
        with patch('backend.routes.analyzer.analyze_code') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "security_issues": [],
                "syntax_errors": [],
                "suggestions": ["Good recursive implementation"],
                "is_safe": True,
                "error": ""
            }
            
            response = self.client.post("/analyze", data={"code": safe_code})
            assert response.status_code == 200
            assert response.json()["is_safe"] is True
    
    def test_complete_workflow_unsafe_code(self):
        """Test the complete workflow with unsafe code"""
        unsafe_code = "import subprocess; subprocess.run(['rm', '-rf', '/'])"
        
        with patch('backend.routes.analyzer.analyze_code') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "security_issues": [
                    {
                        "type": "dangerous_subprocess",
                        "severity": "high",
                        "message": "Dangerous subprocess call"
                    }
                ],
                "syntax_errors": [],
                "suggestions": ["Avoid dangerous system calls"],
                "is_safe": False,
                "error": ""
            }
            
            # Test that analyze-and-compile blocks execution
            response = self.client.post("/analyze-and-compile", data={"code": unsafe_code})
            assert response.status_code == 200
            
            data = response.json()
            assert data["execution"]["success"] is False
            assert "security concerns" in data["execution"]["error"]


# Utility functions for running tests
def run_all_tests():
    """Run all test cases"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    # Run tests when script is executed directly
    run_all_tests()
