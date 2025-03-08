#!/usr/bin/env python3
"""
SPL Interpreter - Optimized Version
"""
import sys
import traceback
from pathlib import Path
from threading import Thread
from typing import Any, Dict, List, Optional

# Import local modules
from runtime import Sandbox 
from .concurrency import spawn
from src.type_checker import TypeChecker
from .custom_builtins import CUSTOM_BUILTINS
from .lexer import Lexer

class SPLRuntimeError(Exception):
    """Base exception for SPL runtime errors"""
    def __init__(self, message: str, node: Optional[Dict] = None):
        super().__init__(message)
        self.node = node
        self.stack_trace: List[str] = []

    def add_stack_frame(self, frame: str) -> None:
        self.stack_trace.append(frame)

class Environment:
    """Enhanced environment with type checking and scoping"""
    def __init__(self, parent: Optional['Environment'] = None, sandbox: bool = False):
        self.vars: Dict[str, Any] = {}
        self.parent = parent
        self.sandbox = Sandbox() if sandbox else None
        self.type_checker = TypeChecker()

    def get(self, name: str) -> Any:
        current = self
        while current:
            if name in current.vars:
                return current.vars[name]
            current = current.parent
        raise SPLRuntimeError(f"Kisichojulikana: {name}")

    def set(self, name: str, value: Any, var_type: Optional[str] = None) -> None:
        if self.sandbox and self.sandbox.is_restricted(name):
            raise SPLRuntimeError(f"Uvunjifu wa sheria: {name}")
            
        if var_type:
            self.type_checker.validate(value, var_type)
            
        self.vars[name] = value

class Interpreter:
    """Main interpreter class with enhanced features"""
    def __init__(self, sandbox: bool = False):
        self.global_env = Environment(sandbox=sandbox)
        self.global_env.vars.update(CUSTOM_BUILTINS)
        self.current_env = self.global_env

    def interpret(self, ast: List[Dict], env: Optional[Environment] = None) -> Any:
        """Execute AST nodes in specified environment"""
        result = None
        original_env = self.current_env
        self.current_env = env or self.current_env
        
        try:
            for node in ast:
                result = self.visit(node)
            return result
        finally:
            self.current_env = original_env

    def visit(self, node: Dict) -> Any:
        """Dispatch node to appropriate method"""
        method_name = f'visit_{node["type"]}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node: Dict) -> None:
        raise SPLRuntimeError(f"Hakuna njia ya {node['type']}", node)

    # Node Visitors
    def visit_Number(self, node: Dict) -> float:
        return node['value']

    def visit_String(self, node: Dict) -> str:
        return node['value']

    def visit_Variable(self, node: Dict) -> Any:
        return self.current_env.get(node['name'])

    def visit_Assignment(self, node: Dict) -> Any:
        value = self.visit(node['value'])
        var_type = node.get('type')
        self.current_env.set(node['name'], value, var_type)
        return value

    def visit_BinaryOp(self, node: Dict) -> Any:
        left = self.visit(node['left'])
        right = self.visit(node['right'])
        op = node['operator']

        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
        }

        if op not in ops:
            raise SPLRuntimeError(f"Operesheni isiyojulikana: {op}", node)

        try:
            return ops[op](left, right)
        except TypeError as e:
            raise SPLRuntimeError(f"Aina si sahihi: {e}", node)

    def visit_FunctionDef(self, node: Dict) -> None:
        def function_wrapper(*args: Any) -> Any:
            local_env = Environment(parent=self.current_env)
            
            # Handle parameters with optional type checking
            for param, arg in zip(node['params'], args):
                param_name = param['name']
                param_type = param.get('type')
                local_env.set(param_name, arg, param_type)

            # Execute function body
            old_env = self.current_env
            self.current_env = local_env
            result = None
            
            try:
                for stmt in node['body']:
                    result = self.visit(stmt)
            finally:
                self.current_env = old_env

            return result

        self.current_env.set(node['name'], function_wrapper)

    def visit_FunctionCall(self, node: Dict) -> Any:
        func = self.visit(node['function'])
        args = [self.visit(arg) for arg in node['args']]
        return func(*args)

    def visit_If(self, node: Dict) -> Any:
        condition = self.visit(node['condition'])
        branch = node['then'] if condition else node.get('else', [])
        return self.interpret(branch, Environment(parent=self.current_env))

    def visit_PatternMatch(self, node: Dict) -> Any:
        value = self.visit(node['expression'])
        
        for case in node['cases']:
            pattern = case['pattern']
            if pattern == '_' or self.match_pattern(pattern, value):
                return self.interpret(case['body'], Environment(parent=self.current_env))
        
        raise SPLRuntimeError("Hakuna mfano ulinganifu", node)

    def match_pattern(self, pattern: Any, value: Any) -> bool:
        """Enhanced pattern matching logic"""
        if isinstance(pattern, dict):
            return self.visit(pattern) == value
        return pattern == value

    def visit_Spawn(self, node: Dict) -> Any:
        def task_wrapper():
            try:
                return self.interpret(node['body'], Environment(parent=self.current_env))
            except Exception as e:
                print(f"Shida ya mtindo: {e}")

        return spawn(task_wrapper)

def start_repl() -> None:
    """Enhanced REPL with syntax highlighting"""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.lexers import PygmentsLexer
    from .lexer import SPLexer

    session = PromptSession(lexer=PygmentsLexer(SPLexer()))
    interpreter = Interpreter()

    print("SPL REPL (Andika 'saidia' au 'ondoka')")
    while True:
        try:
            code = session.prompt(">>> ")
            
            if code.strip().lower() in ('ondoka', 'exit'):
                break
                
            if code.strip().lower() == 'saidia':
                show_help()
                continue
                
            # TODO: Integrate with actual parser
            from .parser import Parser
            tokens = Lexer(code).tokenize()
            ast = Parser(tokens).parse()
            result = interpreter.interpret(ast)
            if result is not None:
                print(result)
                
        except KeyboardInterrupt:
            continue
        except Exception as e:
            print(f"\033[91mShida: {e}\033[0m")

def execute_file(filename: str, sandbox: bool = False) -> None:
    """Execute SPL file with optional sandboxing"""
    from .lexer import Lexer
    from .parser import Parser

    interpreter = Interpreter(sandbox=sandbox)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
            tokens = Lexer(source).tokenize()
            ast = Parser(tokens).parse()
            interpreter.interpret(ast)
            
    except FileNotFoundError:
        raise SPLRuntimeError(f"Faili haipatikani: {filename}")
    except IsADirectoryError:
        raise SPLRuntimeError(f"Ni folda, si faili: {filename}")

def show_help() -> None:
    """Display help information"""
    help_text = """
Msada wa SPL:
  andika()     - Chapisha kwenye skrini
  soma()       - Kumbukumbu kutoka kwa mtumiaji
  pakua()      - Pata data kutoka kwa mtandao
  panga()      - Tekeleza kitendo kwa kila kipengele
  ongeza()     - Chapa jumla ya namba
  nusu()       - Gawanya kwa nusu
  ondoka       - Toka kwenye REPL
    """
    print(help_text)

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            execute_file(sys.argv[1])
        else:
            start_repl()
    except SPLRuntimeError as e:
        print(f"\033[91mShida:\033[0m {e}")
        sys.exit(1)