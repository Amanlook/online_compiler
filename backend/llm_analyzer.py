"""
LLM-powered code analyzer for security, syntax, and quality checks
"""

import json
import ast
import aiohttp
from typing import Dict, Any
import logging
from dotenv import load_dotenv

from .config import (
    LLM_PROVIDER,
    GITHUB_TOKEN,
    LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMCodeAnalyzer:
    """Analyzes Python code using LLM for security, syntax, and quality checks"""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.model = LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        self.timeout = LLM_TIMEOUT
        
        # Setup GitHub Models API
        if GITHUB_TOKEN:
            self.github_token = GITHUB_TOKEN
            self.github_base_url = 'https://models.inference.ai.azure.com'
        else:
            self.github_token = None
            self.github_base_url = None
        
    async def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code for security, syntax, and quality issues
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dict containing analysis results and suggestions
        """
        if not code.strip():
            return {
                "success": False,
                "security_issues": [],
                "syntax_errors": [],
                "suggestions": [],
                "is_safe": False,
                "error": "No code provided"
            }
        
        # First, do basic syntax check
        syntax_check = self._check_syntax(code)
        
        # Then, do security analysis
        security_check = self._check_security_patterns(code)
        
        # Finally, get LLM analysis
        llm_analysis = await self._get_llm_analysis(code)
        
        # Combine all results
        result = {
            "success": True,
            "security_issues": security_check["issues"] + llm_analysis.get("security_issues", []),
            "syntax_errors": syntax_check["errors"],
            "suggestions": llm_analysis.get("suggestions", []),
            "is_safe": syntax_check["valid"] and security_check["safe"] and llm_analysis.get("is_safe", True),
            "fixed_code": llm_analysis.get("fixed_code", ""),
            "explanation": llm_analysis.get("explanation", ""),
            "error": ""
        }
        
        return result
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax using AST parser"""
        try:
            ast.parse(code)
            return {"valid": True, "errors": []}
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [{
                    "type": "syntax",
                    "line": e.lineno,
                    "message": str(e),
                    "severity": "error"
                }]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [{
                    "type": "parsing",
                    "line": 0,
                    "message": f"Parsing error: {str(e)}",
                    "severity": "error"
                }]
            }
    
    def _check_security_patterns(self, code: str) -> Dict[str, Any]:
        """Check for basic security patterns in code"""
        security_issues = []
        
        # List of potentially dangerous patterns
        dangerous_patterns = [
            ("import os", "OS module access"),
            ("import subprocess", "Subprocess module access"),
            ("import sys", "System module access"),
            ("exec(", "Dynamic code execution"),
            ("eval(", "Dynamic code evaluation"),
            ("__import__", "Dynamic imports"),
            ("open(", "File system access"),
            ("input(", "User input - may cause blocking"),
            ("raw_input(", "User input - may cause blocking"),
            ("while True:", "Infinite loop detected"),
            ("for i in range(", "Potential large range loop"),
        ]
        
        for pattern, description in dangerous_patterns:
            if pattern in code:
                security_issues.append({
                    "type": "security",
                    "pattern": pattern,
                    "description": description,
                    "severity": "warning" if pattern in ["input(", "raw_input(", "for i in range("] else "high"
                })
        
        # Check for very large loops
        if "range(" in code:
            try:
                # Simple check for large numbers in range calls
                import re
                range_matches = re.findall(r'range\((\d+)', code)
                for match in range_matches:
                    if int(match) > 10000:
                        security_issues.append({
                            "type": "performance",
                            "pattern": f"range({match})",
                            "description": "Large range detected - may cause timeout",
                            "severity": "warning"
                        })
            except Exception:
                pass
        
        return {
            "safe": len([issue for issue in security_issues if issue["severity"] == "high"]) == 0,
            "issues": security_issues
        }
    
    async def _get_llm_analysis(self, code: str) -> Dict[str, Any]:
        """Get analysis from LLM provider"""
        try:
            if self.provider == "github" or self.provider == "perplexity":  # Default to GitHub Models
                return await self._analyze_with_github_models(code)
            elif self.provider == "openai":
                return self._analyze_with_openai(code)
            elif self.provider == "anthropic":
                return self._analyze_with_anthropic(code)
            elif self.provider == "ollama":
                return self._analyze_with_ollama(code)
            else:
                logger.warning(f"Unknown LLM provider: {self.provider}, defaulting to GitHub Models")
                return await self._analyze_with_github_models(code)
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return {
                "is_safe": True,
                "suggestions": [f"LLM analysis unavailable: {str(e)}"],
                "security_issues": []
            }
    
    async def _analyze_with_github_models(self, code: str) -> Dict[str, Any]:
        """Analyze code using GitHub Models API"""
        if not self.github_token:
            return {"is_safe": True, "suggestions": ["GitHub Models API not configured"], "security_issues": []}
        
        prompt = self._create_analysis_prompt(code)
        
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Python code security and quality analyzer. Respond only with valid JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.1
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.github_base_url}/chat/completions", 
                                       headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return self._parse_llm_response(content)
                    else:
                        error_text = await response.text()
                        logger.error(f"GitHub Models API error: {response.status} - {error_text}")
                        return {"is_safe": True, "suggestions": ["GitHub Models analysis failed"], "security_issues": []}
                        
        except Exception as e:
            logger.error(f"GitHub Models API error: {str(e)}")
            return {"is_safe": True, "suggestions": ["GitHub Models analysis failed"], "security_issues": []}
    
    def _analyze_with_openai(self, code: str) -> Dict[str, Any]:
        """Analyze code using OpenAI API"""
        # Similar implementation for OpenAI
        return {"is_safe": True, "suggestions": ["OpenAI analysis not implemented"], "security_issues": []}
    
    def _analyze_with_anthropic(self, code: str) -> Dict[str, Any]:
        """Analyze code using Anthropic API"""
        # Similar implementation for Anthropic
        return {"is_safe": True, "suggestions": ["Anthropic analysis not implemented"], "security_issues": []}
    
    def _analyze_with_ollama(self, code: str) -> Dict[str, Any]:
        """Analyze code using Ollama local API"""
        # Similar implementation for Ollama
        return {"is_safe": True, "suggestions": ["Ollama analysis not implemented"], "security_issues": []}
    
    def _create_analysis_prompt(self, code: str) -> str:
        """Create the analysis prompt for the LLM"""
        return f"""
Analyze this Python code for security vulnerabilities, potential issues, and suggest improvements.
Respond with a JSON object containing:
- "is_safe": boolean (true if code is safe to execute)
- "security_issues": array of security concerns with "type", "description", "severity"
- "suggestions": array of improvement suggestions
- "fixed_code": string with improved version of code (if fixes needed)
- "explanation": string explaining the analysis

Code to analyze:
```python
{code}
```

Focus on:
1. Security vulnerabilities (file access, network calls, dangerous imports)
2. Infinite loops or performance issues
3. Syntax improvements
4. Best practices

Respond only with valid JSON, no additional text.
"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract analysis results"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Parse JSON
            result = json.loads(response)
            
            # Validate required fields
            required_fields = ["is_safe", "security_issues", "suggestions"]
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field != "is_safe" else True
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response}")
            return {
                "is_safe": True,
                "security_issues": [],
                "suggestions": ["LLM response parsing failed"],
                "fixed_code": "",
                "explanation": f"Could not parse analysis: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return {
                "is_safe": True,
                "security_issues": [],
                "suggestions": ["LLM analysis processing failed"],
                "fixed_code": "",
                "explanation": f"Analysis error: {str(e)}"
            }
