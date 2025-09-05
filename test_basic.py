"""
Basic test cases that can be run immediately
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        from backend.app import create_app
        from backend.compiler import PythonCompiler  
        from backend.llm_analyzer import LLMCodeAnalyzer
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that FastAPI app can be created"""
    try:
        from backend.app import create_app
        app = create_app()
        assert app is not None
        print("✅ FastAPI app creation successful")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_compiler_initialization():
    """Test that PythonCompiler can be initialized"""
    try:
        from backend.compiler import PythonCompiler
        compiler = PythonCompiler()
        assert compiler is not None
        assert hasattr(compiler, 'execute_code')
        print("✅ PythonCompiler initialization successful")
        return True
    except Exception as e:
        print(f"❌ Compiler initialization error: {e}")
        return False

def test_analyzer_initialization():
    """Test that LLMCodeAnalyzer can be initialized"""
    try:
        from backend.llm_analyzer import LLMCodeAnalyzer
        analyzer = LLMCodeAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_code')
        print("✅ LLMCodeAnalyzer initialization successful")
        return True
    except Exception as e:
        print(f"❌ Analyzer initialization error: {e}")
        return False

async def test_compiler_empty_code():
    """Test compiler with empty code input"""
    try:
        from backend.compiler import PythonCompiler
        compiler = PythonCompiler()
        result = await compiler.execute_code("")
        
        assert result["success"] is False
        assert result["error"] == "No code provided"
        print("✅ Compiler empty code test successful")
        return True
    except Exception as e:
        print(f"❌ Compiler empty code test error: {e}")
        return False

async def test_analyzer_empty_code():
    """Test analyzer with empty code input"""
    try:
        from backend.llm_analyzer import LLMCodeAnalyzer
        analyzer = LLMCodeAnalyzer()
        result = await analyzer.analyze_code("")
        
        assert result["success"] is False
        assert result["error"] == "No code provided"
        assert result["is_safe"] is False
        print("✅ Analyzer empty code test successful")
        return True
    except Exception as e:
        print(f"❌ Analyzer empty code test error: {e}")
        return False

def run_basic_tests():
    """Run all basic tests"""
    print("🧪 Running basic test suite...")
    print("="*50)
    
    tests = [
        ("Import Test", test_imports),
        ("App Creation Test", test_app_creation),
        ("Compiler Initialization Test", test_compiler_initialization),
        ("Analyzer Initialization Test", test_analyzer_initialization),
    ]
    
    async_tests = [
        ("Compiler Empty Code Test", test_compiler_empty_code),
        ("Analyzer Empty Code Test", test_analyzer_empty_code),
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n🔸 Running {test_name}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    # Run asynchronous tests
    for test_name, test_func in async_tests:
        print(f"\n🔸 Running {test_name}...")
        try:
            if asyncio.run(test_func()):
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    run_basic_tests()
