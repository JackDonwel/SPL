#!/usr/bin/env python3
"""
SPL Compiler - Optimized Version
"""
from pathlib import Path
import llvmlite.ir as llir
import llvmlite.binding as llvm
from typing import Dict, Any, Optional
from src.lexer import Lexer
from src.parser import Parser

class Compiler:
    """Compiles SPL code to various targets with enhanced error handling"""
    
    def __init__(self, source: str):
        self.source = source
        self.ast: Optional[list] = None
        self._llvm_initialized = False
        self._init_llvm()

    def _init_llvm(self) -> None:
        """Initialize LLVM infrastructure once"""
        if not self._llvm_initialized:
            llvm.initialize()
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
            self._llvm_initialized = True
            
        self.module = llir.Module(name="spl_module")
        self.builder: Optional[llir.IRBuilder] = None

    def _validate_ast(self) -> None:
        """Ensure AST is properly structured"""
        if not isinstance(self.ast, list):
            raise ValueError("Invalid AST: Expected list of nodes")
        if len(self.ast) == 0:
            raise ValueError("Empty AST: No nodes to compile")

    def _transpile_node(self, node: Dict[str, Any], indent: int = 0) -> str:
        """Recursive Python code generation with enhanced node support"""
        space = " " * indent
        
        # Function definition
        if node["type"] == "FunctionDef":
            params = ", ".join(
                f"{p['name']}: {p.get('type', 'Any')}"
                for p in node["params"]
            )
            code = f"{space}def {node['name']}({params}) -> {node.get('return_type', 'None')}:\n"
            code += "".join(
                self._transpile_node(stmt, indent + 4)
                for stmt in node["body"]
            )
            return code
            
        # Pattern matching
        if node["type"] == "PatternMatch":
            expr = self._transpile_node(node["expression"])
            code = f"{space}match {expr}:\n"
            for case in node["cases"]:
                pattern = "_" if case["pattern"] == "_" else self._transpile_node(case["pattern"])
                code += f"{space}    case {pattern}:\n"
                code += "".join(
                    self._transpile_node(stmt, indent + 8)
                    for stmt in case["body"]
                )
            return code
            
        # Binary operations
        if node["type"] == "BinaryOp":
            left = self._transpile_node(node["left"])
            right = self._transpile_node(node["right"])
            return f"({left} {node['operator']} {right})"
            
        # Function calls
        if node["type"] == "FunctionCall":
            args = ", ".join(self._transpile_node(arg) for arg in node["args"])
            return f"{node['function']['name']}({args})"
            
        # Variables and literals
        if node["type"] in ("Number", "String", "Var"):
            return str(node["value"])

        raise NotImplementedError(f"Unsupported node type: {node['type']}")

    def _generate_llvm_ir(self, node: Dict[str, Any]) -> None:
        """LLVM IR generation with basic block management"""
        if node["type"] == "FunctionDef":
            ret_type = self._llvm_type_map(node.get("return_type", "int"))
            param_types = [self._llvm_type_map(p["type"]) for p in node["params"]]
            
            func_type = llir.FunctionType(ret_type, param_types)
            function = llir.Function(self.module, func_type, name=node["name"])
            
            entry_block = function.append_basic_block("entry")
            self.builder = llir.IRBuilder(entry_block)
            
            # Process function body
            for stmt in node["body"]:
                self._generate_llvm_ir(stmt)
                
            # Add implicit return for void functions
            if not self.builder.block.is_terminated:
                self.builder.ret(llir.Constant(ret_type, 0))

        elif node["type"] == "BinaryOp":
            left = self._generate_llvm_ir(node["left"])
            right = self._generate_llvm_ir(node["right"])
            op = node["operator"]
            
            if op == '+':
                return self.builder.add(left, right, "addtmp")
            elif op == '-':
                return self.builder.sub(left, right, "subtmp")
            elif op == '*':
                return self.builder.mul(left, right, "multmp")
            elif op == '/':
                return self.builder.sdiv(left, right, "divtmp")
            else:
                raise ValueError(f"Unsupported LLVM operator: {op}")

    def _llvm_type_map(self, type_hint: str) -> llir.Type:
        """Map SPL types to LLVM types with validation"""
        type_map = {
            "int": llir.IntType(32),
            "float": llir.DoubleType(),
            "str": llir.PointerType(llir.IntType(8)),
            "void": llir.VoidType()
        }
        
        if type_hint not in type_map:
            raise ValueError(f"Unsupported type: {type_hint}")
        return type_map[type_hint]

    def compile(self, target: str = "python") -> str:
        """Compile SPL source to specified target format"""
        try:
            # Parse source code
            lexer = Lexer(self.source)
            parser = Parser(lexer.tokenize())
            self.ast = parser.parse()
            
            self._validate_ast()
            
            # Dispatch to compilation target
            if target == "python":
                return self._transpile_to_python()
            elif target == "llvm":
                return self._generate_llvm()
            elif target == "wat":
                return self._generate_wasm()
            else:
                raise ValueError(f"Unsupported target: {target}")
                
        except Exception as e:
            raise RuntimeError(f"Compilation failed: {str(e)}") from e

    def _transpile_to_python(self) -> str:
        """Generate Python code with proper formatting"""
        header = "# Generated Python code from SPL\n\n"
        header += "from typing import Any, Match\n\n"
        return header + "\n".join(
            self._transpile_node(node) 
            for node in self.ast
        )

    def _generate_llvm(self) -> str:
        """Generate LLVM IR with module validation"""
        for node in self.ast:
            self._generate_llvm_ir(node)
            
        # Validate generated module
        llvm.parse_assembly(str(self.module))
        return str(self.module)

    def _generate_wasm(self) -> str:
        """Generate WebAssembly text format (WAT)"""
        wat = "(module\n"
        for node in self.ast:
            if node["type"] == "FunctionDef":
                wat += f'  (func ${node["name"]}\n'
                wat += f'    (export "{node["name"]}")\n'
                # Add parameters and body here
                wat += "  )\n"
        wat += ")"
        return wat

if __name__ == "__main__":
    sample_code = """
kazi jumlisha(a: int, b: int) -> int {
    rudisha a + b
}
    """.strip()

    try:
        compiler = Compiler(sample_code)
        
        print("Python Transpilation:")
        print(compiler.compile("python"))
        
        print("\nLLVM IR:")
        print(compiler.compile("llvm"))
        
        print("\nWebAssembly Text:")
        print(compiler.compile("wat"))
        
    except RuntimeError as e:
        print(f"Compiler Error: {e}\n")
        if e.__cause__:
            print(f"Caused by: {e.__cause__}")