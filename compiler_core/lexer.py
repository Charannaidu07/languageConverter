import re
from .tokens import Token, TokenType

# Basic regex for tokens
TOKEN_REGEX = {
    'comments': r'//.*|/\*[\s\S]*?\*/',
    'preprocessor': r'#.*',
    'keywords': r'\b(int|float|string|void|if|else|while|for|return|print|let|def)\b',
    'identifiers': r'[a-zA-Z_]\w*',
    'float_lit': r'\d+\.\d+',
    'int_lit': r'\d+',
    'string_lit': r'"[^"]*"',
    'operators': r'==|!=|<=|>=|\+|-|\*|/|=|<|>',
    'delimiters': r'\(|\)|\{|\}|;|:|,|\[|\]',
    'whitespace': r'\s+',
}

KEYWORD_MAP = {
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'string': TokenType.STRING,
    'void': TokenType.VOID,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'return': TokenType.RETURN,
    'print': TokenType.PRINT,
    'let': TokenType.LET,
    'def': TokenType.DEF,
}

OPERATOR_MAP = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MUL,
    '/': TokenType.DIV,
    '=': TokenType.ASSIGN,
    '==': TokenType.EQ,
    '!=': TokenType.NEQ,
    '<': TokenType.LT,
    '>': TokenType.GT,
    '<=': TokenType.LTE,
    '>=': TokenType.GTE,
}

DELIMITER_MAP = {
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET, # Need to add in tokens.py too, but we can avoid crash by parsing it.
    ']': TokenType.RBRACKET,
    ';': TokenType.SEMICOLON,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
}

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, code: str, language: str):
        # Unwrap Java Class Structures
        import re
        code = re.sub(r'public\s+class\s+\w+\s*\{', '', code)
        code = re.sub(r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s*\w+\s*\)', 'void main()', code)
        # Unwrap C++ namespaces
        code = re.sub(r'using\s+namespace\s+[a-zA-Z0-9_]+\s*;', '', code)
        
        # Normalize language-specific print mechanisms into standard function calls
        # so our simple parser can handle them as identifiers.
        code = code.replace("System.out.println", "printJava")
        code = code.replace("System.out.print", "printJava")
        # Normalize C++ cout streams
        import re
        code = re.sub(r'(?:std::)?cout\s*<<\s*([^;<]+)(?:<<.*?)*;', r'printCpp(\1);', code)
        
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []
        self.language = language # 'c', 'cpp', 'java', 'minilang'

    def append_token(self, type_, value):
        self.tokens.append(Token(type_, value, self.line))

    def tokenize(self):
        # Master regex
        master_pat = re.compile(
            rf"(?P<comments>{TOKEN_REGEX['comments']})|"
            rf"(?P<preprocessor>{TOKEN_REGEX['preprocessor']})|"
            rf"(?P<whitespace>{TOKEN_REGEX['whitespace']})|"
            rf"(?P<float_lit>{TOKEN_REGEX['float_lit']})|"
            rf"(?P<int_lit>{TOKEN_REGEX['int_lit']})|"
            rf"(?P<string_lit>{TOKEN_REGEX['string_lit']})|"
            rf"(?P<keyword>{TOKEN_REGEX['keywords']})|"
            rf"(?P<identifier>{TOKEN_REGEX['identifiers']})|"
            rf"(?P<operator>{TOKEN_REGEX['operators']})|"
            rf"(?P<delimiter>{TOKEN_REGEX['delimiters']})"
        )

        pos = 0
        while pos < len(self.code):
            match = master_pat.match(self.code, pos)
            if match:
                type_ = match.lastgroup
                val = match.group(type_)
                
                if type_ in ('whitespace', 'comments'):
                    self.line += val.count('\n')
                elif type_ == 'preprocessor':
                    pass # ignore preprocessor
                elif type_ == 'keyword':
                    # some protection for language specific keywords
                    if self.language != 'minilang' and val in ['let', 'def']:
                        self.append_token(TokenType.IDENTIFIER, val)
                    else:
                        self.append_token(KEYWORD_MAP[val], val)
                elif type_ == 'identifier':
                    # re-check keyword just in case the regex missed it because of word boundaries
                    if val in KEYWORD_MAP and (self.language == 'minilang' or val not in ['let', 'def']):
                         self.append_token(KEYWORD_MAP[val], val)
                    else:
                        self.append_token(TokenType.IDENTIFIER, val)
                elif type_ == 'float_lit':
                    self.append_token(TokenType.FLOAT_LIT, val)
                elif type_ == 'int_lit':
                    self.append_token(TokenType.INTEGER_LIT, val)
                elif type_ == 'string_lit':
                    self.append_token(TokenType.STRING_LIT, val[1:-1])
                elif type_ == 'operator':
                    self.append_token(OPERATOR_MAP[val], val)
                elif type_ == 'delimiter':
                    self.append_token(DELIMITER_MAP[val], val)
                
                pos = match.end()
            else:
                raise LexerError(f"Illegal character at line {self.line}: '{self.code[pos]}'")

        self.append_token(TokenType.EOF, "")
        return self.tokens
