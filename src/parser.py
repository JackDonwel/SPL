#!/usr/bin/env python3
"""
SPL Parser - Enhanced Version
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int

class ParserError(Exception):
    """Custom parser error with location information"""
    def __init__(self, message: str, token: Token):
        super().__init__(
            f"{message} at line {token.line}, column {token.column}"
        )
        self.token = token

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_line = 1
        self.current_column = 1

    @property
    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        token = self.current_token
        self.pos += 1
        self.current_line = token.line
        self.current_column = token.column
        return token

    def consume(self, expected_type: str, expected_value: Optional[str] = None) -> Token:
        token = self.current_token
        if token.type != expected_type:
            raise ParserError(
                f"Unexpected token type '{token.type}', expected '{expected_type}'", 
                token
            )
            
        if expected_value is not None and token.value != expected_value:
            raise ParserError(
                f"Unexpected value '{token.value}', expected '{expected_value}'", 
                token
            )
            
        return self.advance()

    def parse(self) -> List[Dict[str, Any]]:
        """Parse complete program into AST"""
        ast = []
        while self.current_token.type != 'EOF':
            ast.append(self.parse_statement())
        return ast

    def parse_statement(self) -> Dict[str, Any]:
        """Parse top-level statements"""
        token = self.current_token
        
        if token.type == 'KEYWORD':
            return {
                'kazi': self.parse_function_def,
                'chapisha': self.parse_print,
                'lingana': self.parse_pattern_match,
            }[token.value]()
            
        return self.parse_expression_statement()

    def parse_function_def(self) -> Dict[str, Any]:
        """Parse function definition with full type support"""
        start_token = self.consume('KEYWORD', 'kazi')
        name = self.consume('IDENTIFIER').value
        params = self.parse_parameter_list()
        return_type = self.parse_return_type()
        body = self.parse_block()
        
        return {
            'type': 'FunctionDef',
            'name': name,
            'params': params,
            'return_type': return_type,
            'body': body,
            'loc': self.get_location(start_token)
        }

    def parse_parameter_list(self) -> List[Dict[str, str]]:
        """Parse typed parameter list"""
        self.consume('LPAREN')
        params = []
        
        while self.current_token.type != 'RPAREN':
            name = self.consume('IDENTIFIER').value
            self.consume('COLON')
            param_type = self.parse_type()
            params.append({'name': name, 'type': param_type})
            
            if self.current_token.type != 'COMMA':
                break
            self.consume('COMMA')
            
        self.consume('RPAREN')
        return params

    def parse_return_type(self) -> Optional[str]:
        """Parse optional return type annotation"""
        if self.current_token.type == 'OPERATOR' and self.current_token.value == '->':
            self.advance()
            return self.parse_type()
        return None

    def parse_type(self) -> str:
        """Parse type annotations"""
        if self.current_token.type == 'IDENTIFIER':
            return self.advance().value
        raise ParserError("Invalid type specification", self.current_token)

    def parse_print(self) -> Dict[str, Any]:
        """Parse print statement with expression"""
        start_token = self.consume('KEYWORD', 'chapisha')
        value = self.parse_expression()
        self.consume_newlines()
        return {
            'type': 'Print',
            'value': value,
            'loc': self.get_location(start_token)
        }

    def parse_pattern_match(self) -> Dict[str, Any]:
        """Parse pattern matching with full block support"""
        start_token = self.consume('KEYWORD', 'lingana')
        subject = self.parse_expression()
        cases = []
        
        self.consume('LBRACE')
        while self.current_token.type != 'RBRACE':
            pattern = self.parse_pattern()
            self.consume('OPERATOR', '=>')
            body = self.parse_block() if self.current_token.type == 'LBRACE' \
                else [self.parse_statement()]
            cases.append({'pattern': pattern, 'body': body})
            self.consume_newlines()
            
        self.consume('RBRACE')
        return {
            'type': 'PatternMatch',
            'expression': subject,
            'cases': cases,
            'loc': self.get_location(start_token)
        }

    def parse_pattern(self) -> Dict[str, Any]:
        """Parse match patterns with type support"""
        token = self.current_token
        
        if token.type == 'NUMBER':
            return {'type': 'Literal', 'value': self.advance().value}
            
        if token.type == 'STRING':
            return {'type': 'Literal', 'value': self.advance().value}
            
        if token.value == '_':
            self.advance()
            return {'type': 'Wildcard'}
            
        if token.type == 'IDENTIFIER':
            name = self.advance().value
            if self.current_token.type == 'COLON':
                self.consume('COLON')
                pattern_type = self.parse_type()
                return {'type': 'TypedPattern', 'name': name, 'annotation': pattern_type}
            return {'type': 'Binding', 'name': name}
            
        raise ParserError("Invalid pattern syntax", token)

    def parse_block(self) -> List[Dict[str, Any]]:
        """Parse statement blocks with proper scope handling"""
        if self.current_token.type == 'LBRACE':
            return self.parse_braced_block()
        return [self.parse_statement()]

    def parse_braced_block(self) -> List[Dict[str, Any]]:
        """Parse { ... } block with multiple statements"""
        self.consume('LBRACE')
        statements = []
        
        while self.current_token.type not in ('RBRACE', 'EOF'):
            statements.append(self.parse_statement())
            self.consume_newlines()
            
        self.consume('RBRACE')
        return statements

    def parse_expression_statement(self) -> Dict[str, Any]:
        """Parse expression as statement"""
        expr = self.parse_expression()
        self.consume_newlines()
        return expr

    def parse_expression(self) -> Dict[str, Any]:
        """Parse full expression with operator precedence"""
        return self.parse_binary_expression(0)

    def parse_binary_expression(self, precedence: int) -> Dict[str, Any]:
        """Handle operator precedence using precedence climbing"""
        ops_precedence = {
            '+': 2, '-': 2,
            '*': 3, '/': 3,
            '==': 1, '!=': 1,
            '>': 1, '<': 1, '>=': 1, '<=': 1
        }
        
        left = self.parse_primary()
        
        while True:
            token = self.current_token
            if token.type != 'OPERATOR' or ops_precedence.get(token.value, 0) <= precedence:
                break
                
            op = self.advance().value
            right = self.parse_binary_expression(ops_precedence[op])
            left = {
                'type': 'BinaryOp',
                'operator': op,
                'left': left,
                'right': right,
                'loc': self.get_location(token)
            }
            
        return left

    def parse_primary(self) -> Dict[str, Any]:
        """Parse primary expressions with location tracking"""
        token = self.current_token
        loc = self.get_location(token)
        
        if token.type == 'NUMBER':
            return self.parse_number(loc)
            
        if token.type == 'STRING':
            return self.parse_string(loc)
            
        if token.type == 'IDENTIFIER':
            return self.parse_identifier(loc)
            
        if token.type == 'LPAREN':
            return self.parse_parenthesized(loc)
            
        raise ParserError("Unexpected expression", token)

    def parse_number(self, loc: Dict) -> Dict[str, Any]:
        value = self.advance().value
        return {'type': 'Number', 'value': value, 'loc': loc}

    def parse_string(self, loc: Dict) -> Dict[str, Any]:
        value = self.advance().value
        return {'type': 'String', 'value': value, 'loc': loc}

    def parse_identifier(self, loc: Dict) -> Dict[str, Any]:
        name = self.advance().value
        
        if self.current_token.type == 'LPAREN':
            return self.parse_function_call(name, loc)
            
        return {'type': 'Var', 'name': name, 'loc': loc}

    def parse_function_call(self, name: str, loc: Dict) -> Dict[str, Any]:
        self.consume('LPAREN')
        args = []
        
        while self.current_token.type != 'RPAREN':
            args.append(self.parse_expression())
            if self.current_token.type != 'COMMA':
                break
            self.consume('COMMA')
            
        self.consume('RPAREN')
        return {
            'type': 'FunctionCall',
            'function': {'type': 'Var', 'name': name, 'loc': loc},
            'args': args,
            'loc': loc
        }

    def parse_parenthesized(self, loc: Dict) -> Dict[str, Any]:
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('RPAREN')
        return expr

    def consume_newlines(self):
        """Consume trailing newlines"""
        while self.current_token.type == 'NEWLINE':
            self.advance()

    def get_location(self, token: Token) -> Dict[str, int]:
        return {
            'start_line': token.line,
            'start_col': token.column,
            'end_line': self.current_line,
            'end_col': self.current_column
        }

# Example usage remains similar but with proper Token class