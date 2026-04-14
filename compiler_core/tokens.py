from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    PRINT = auto()
    LET = auto() # minilang specific
    DEF = auto() # minilang specific
    
    # Identifiers and Literals
    IDENTIFIER = auto()
    INTEGER_LIT = auto()
    FLOAT_LIT = auto()
    STRING_LIT = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()
    
    EOF = auto()

class Token:
    def __init__(self, type_: TokenType, value: str, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line})"
