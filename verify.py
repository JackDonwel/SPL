#!/usr/bin/env python3
from __future__ import annotations

import unittest
import sys
import traceback
from pathlib import Path
from importlib import import_module
from termcolor import cprint

MODULES = [
    # Core Components
    ("src.lexer", ["Lexer"]),
    ("src.parser", ["Parser"]),
    ("src.interpreter", ["Interpreter", "execute_file", "start_repl"]),
    ("src.compiler", ["Compiler"]),
    ("src.runtime", ["Environment", "Sandbox"]),
    ("src.type_checker", ["TypeChecker"]),
    
    # Concurrency & Utilities
    ("src.concurrency", ["spawn"]),
    ("src.custom_builtins", ["CUSTOM_BUILTINS"]),
    ("src.visual_debugger", ["VisualDebugger"]),
    
    # Infrastructure
    ("src.cli", ["main"]),
    ("src.exceptions", ["SPLRuntimeError"]),
    ("src.version", ["__version__"]),
    
    # Optional Components
    ("src.optimizer", ["optimize_ast"]),  # NIKISAHAU {muhim} 
    ("src.ffi", ["NativeBinding"])        # Kama nikiasahau kuweka hii file
]

class TestImports(unittest.TestCase):
    """Validates all project modules and key components"""
    
    def test_module_imports(self):
        """Verify module imports and required components"""
        for module_path, required in MODULES:
            with self.subTest(module=module_path):
                try:
                    module = import_module(module_path)
                    for item in required:
                        self.assertTrue(
                            hasattr(module, item),
                            f"Missing {item} in {module_path}"
                        )
                    cprint(f"✓ {module_path.ljust(20)} {', '.join(required)}", "green")
                except Exception as e:
                    cprint(f"✗ {module_path}: {str(e)}", "red")
                    traceback.print_exc()
                    raise

    def test_syntax(self):
        """Check for syntax errors in all source files"""
        for path in Path("src").rglob("*.py"):
            with self.subTest(file=path), open(path) as f:
                content = f.read()
                try:
                    compile(content, str(path), 'exec')
                    cprint(f"✓ Syntax OK: {path}", "green")
                except Exception as e:
                    cprint(f"✗ Syntax error in {path}: {e}", "red")
                    raise

if __name__ == "__main__":
    print("🧪 SPL Module Verification")
    print(f"Python {sys.version.split()[0]}")
    print(f"Testing {len(MODULES)} modules...\n")
    
    try:
        unittest.main(verbosity=2, exit=False)
    except SystemExit:
        pass
    
    print("\n🔍 Verification Summary:")
    print(f"- {len(MODULES)} core modules checked")
    print(f"- {len(list(Path('src').rglob('*.py')))} source files validated")
