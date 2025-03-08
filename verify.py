import unittest
from importlib import import_module

MODULES = [
    "src.lexer",
    "src.parser",
    "src.interpreter",
    "src.compiler",
    "src.concurrency"
]

class TestImports(unittest.TestCase):
    def test_module_imports(self):
        for module in MODULES:
            with self.subTest(module=module):
                import_module(module)

if __name__ == "__main__":
    unittest.main()