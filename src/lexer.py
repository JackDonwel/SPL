#!/usr/bin/env python3
"""
SPL Lexer - Enhanced Version
"""
import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"{self.type}:{self.value} ({self.line}:{self.column})"

class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column

SWAHILI_KEYWORDS = {
    'kazi': 'FUNCTION',
    'rudisha': 'RETURN',
    'kama': 'IF',
    'vinginevyo': 'ELSE',
    'kwa': 'FOR',
    'wakati': 'WHILE',
    'chapisha': 'PRINT',
    'aina': 'TYPE',
    'lingana': 'MATCH',
    'anzisha': 'SPAWN',
    'badili': 'MUT',
    'kutoka': 'FROM',
    'ambapo': 'WHERE',
    'chagua': 'SELECT',
    'kweli': 'TRUE',
    'sikweli': 'FALSE',
    'hakuna': 'NONE'
}

OPERATOR_MAP = {
    '==': 'EQ',
    '!=': 'NEQ',
    '<=': 'LTE',
    '>=': 'GTE',
    '=>': 'FAT_ARROW',
    '->': 'THIN_ARROW',
    '|>': 'PIPE',
}

class SPLexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.indent_stack = [0]
        self.tokens: List[Token] = []
        self.current_indent = 0

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.handle_line()
        
        self.handle_dedents()
        self.add_token('EOF', '')
        return self.tokens

    def handle_line(self):
        self.current_indent = self.calculate_indent()
        self.handle_indentation()
        
        while not self.is_newline():
            if self.peek() == '#':
                self.skip_comment()
                break
                
            token = self.next_token()
            if token:
                self.tokens.append(token)
        
        self.advance_line()

    def calculate_indent(self) -> int:
        indent = 0
        while self.peek() in (' ', '\t'):
            if self.peek() == '\t':
                raise LexerError("Tabs not allowed for indentation", self.line, self.col)
            indent += 1
            self.advance()
        return indent

    def handle_indentation(self):
        if self.current_indent > self.indent_stack[-1]:
            self.indent_stack.append(self.current_indent)
            self.add_token('INDENT', '')
        else:
            while self.current_indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.add_token('DEDENT', '')

    def next_token(self) -> Optional[Token]:
        char = self.peek()
        
        # Handle multi-character operators first
        for op in OPERATOR_MAP:
            if self.source.startswith(op, self.pos):
                return self.make_token(OPERATOR_MAP[op], op)
        
        if char.isdigit():
            return self.read_number()
        if char in ('"', "'"):
            return self.read_string()
        if char.isalpha() or char == '_':
            return self.read_identifier()
        if char in {'+', '-', '*', '/', '=', '<', '>', '!', '|'}:
            return self.make_token('OPERATOR', char)
        if char in {'(', ')', '{', '}', ':', ',', '[', ']'}:
            return self.make_token(char, char)
        
        raise LexerError(f"Unexpected character '{char}'", self.line, self.col)

    def read_number(self) -> Token:
        start = self.pos
        is_float = False
        while self.peek().isdigit() or self.peek() == '.':
            if self.peek() == '.':
                if is_float:
                    break
                is_float = True
            self.advance()
        value = self.source[start:self.pos]
        return self.make_token('FLOAT' if is_float else 'INTEGER', value)

    def read_string(self) -> Token:
        quote = self.peek()
        self.advance()
        start = self.pos
        escape = False
        
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == quote:
                value = self.source[start:self.pos]
                self.advance()
                return self.make_token('STRING', value)
            
            self.advance()
        
        raise LexerError("Unterminated string literal", self.line, self.col)

    def read_identifier(self) -> Token:
        start = self.pos
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        value = self.source[start:self.pos]
        return self.make_token(
            SWAHILI_KEYWORDS.get(value, 'IDENTIFIER'),
            value
        )

    def make_token(self, type_: str, value: str) -> Token:
        token = Token(type_, value, self.line, self.col)
        self.col += len(value)
        self.pos += len(value)
        return token

    def skip_comment(self):
        while self.peek() not in ('\n', '\r'):
            self.advance()

    def advance(self):
        if self.peek() == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1

    def advance_line(self):
        while self.pos < len(self.source) and self.is_newline():
            self.advance()
        self.col = 1

    def is_newline(self) -> bool:
        return self.source[self.pos] in ('\n', '\r')

    def peek(self) -> str:
        return self.source[self.pos] if self.pos < len(self.source) else ''

    def add_token(self, type_: str, value: str):
        self.tokens.append(Token(type_, value, self.line, self.col))

    def handle_dedents(self):
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.add_token('DEDENT', '')

if __name__ == '__main__':
    sample_code = """
kazi jumla(a: nambari, b: nambari) -> nambari {
    rudisha a + b
}

chapisha(jumla(5, 3.2))  # Chapisha jumla
    """.strip()

    lexer = SPLexer(sample_code)
    tokens = lexer.tokenize()
    
    print("Generated Tokens:")
    for token in tokens:
        print(token)
        
    