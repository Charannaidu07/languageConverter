from .tokens import TokenType
from .ast_nodes import *

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1] # EOF

    def advance(self):
        token = self.current()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def match(self, expect_type):
        if self.current().type == expect_type:
            return self.advance()
        raise ParseError(f"Expected {expect_type.name} but got {self.current().type.name} at line {self.current().line}")

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def parse(self):
        statements = []
        while self.current().type != TokenType.EOF:
            if self.current().type == TokenType.RBRACE:
                self.advance() # Ignore stray closing braces left from Java wrapper stripping
                continue
            statements.append(self.parse_declaration())
        return Program(statements)

    def parse_declaration(self):
        tok = self.current()
        if tok.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.VOID):
            # Could be a variable or function
            var_type = self.advance().value
            name = self.match(TokenType.IDENTIFIER).value
            
            if self.current().type == TokenType.LPAREN:
                return self.parse_function(var_type, name)
            else:
                return self.parse_var_decl(var_type, name)
        elif tok.type == TokenType.DEF:
            # Minilang function
            self.advance()
            name = self.match(TokenType.IDENTIFIER).value
            return self.parse_function("auto", name)
        elif tok.type == TokenType.LET:
            self.advance()
            name = self.match(TokenType.IDENTIFIER).value
            return self.parse_var_decl("auto", name)
        else:
            return self.parse_statement()

    def parse_function(self, return_type, name):
        self.match(TokenType.LPAREN)
        params = []
        if self.current().type != TokenType.RPAREN:
            params.append(self.parse_param())
            while self.current().type == TokenType.COMMA:
                self.advance()
                params.append(self.parse_param())
        self.match(TokenType.RPAREN)
        
        self.match(TokenType.LBRACE)
        body = self.parse_block()
        return FunctionDecl(return_type, name, params, body)

    def parse_param(self):
        tok = self.current()
        if tok.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING):
            p_type = self.advance().value
            p_name = self.match(TokenType.IDENTIFIER).value
            return (p_type, p_name)
        else:
            # Minilang parameter without type
            p_name = self.match(TokenType.IDENTIFIER).value
            return ("auto", p_name)

    def parse_var_decl(self, var_type, name):
        init = None
        if self.current().type == TokenType.ASSIGN:
            self.advance()
            init = self.parse_expression()
        self.match(TokenType.SEMICOLON)
        return VarDecl(var_type, name, init)

    def parse_block(self):
        stmts = []
        while self.current().type != TokenType.RBRACE and self.current().type != TokenType.EOF:
            stmts.append(self.parse_statement())
        self.match(TokenType.RBRACE)
        return Block(stmts)

    def parse_statement(self):
        tok = self.current()
        if tok.type == TokenType.IF:
            return self.parse_if()
        elif tok.type == TokenType.WHILE:
            return self.parse_while()
        elif tok.type == TokenType.FOR:
            return self.parse_for()
        elif tok.type == TokenType.PRINT:
            return self.parse_print()
        elif tok.type == TokenType.RETURN:
            return self.parse_return()
        elif tok.type == TokenType.INC:
            self.advance()
            name = self.match(TokenType.IDENTIFIER).value
            self.match(TokenType.SEMICOLON)
            return Assignment(name, BinOp(Identifier(name), "+", Literal(1, 'int')))
        elif tok.type == TokenType.DEC:
            self.advance()
            name = self.match(TokenType.IDENTIFIER).value
            self.match(TokenType.SEMICOLON)
            return Assignment(name, BinOp(Identifier(name), "-", Literal(1, 'int')))
        elif tok.type == TokenType.IDENTIFIER:
            # Could be assignment or func call
            name = self.advance().value
            if self.current().type == TokenType.ASSIGN:
                self.advance()
                expr = self.parse_expression()
                self.match(TokenType.SEMICOLON)
                return Assignment(name, expr)
            elif self.current().type == TokenType.INC:
                self.advance()
                self.match(TokenType.SEMICOLON)
                return Assignment(name, BinOp(Identifier(name), "+", Literal(1, 'int')))
            elif self.current().type == TokenType.DEC:
                self.advance()
                self.match(TokenType.SEMICOLON)
                return Assignment(name, BinOp(Identifier(name), "-", Literal(1, 'int')))
            elif self.current().type == TokenType.LPAREN:
                self.advance()
                args = []
                if self.current().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    while self.current().type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse_expression())
                self.match(TokenType.RPAREN)
                self.match(TokenType.SEMICOLON)
                return FuncCall(name, args)
            else:
                raise ParseError(f"Unexpected token after identifier at line {tok.line}")
        else:
            # Might be a declaration inside a block
            if tok.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.DEF, TokenType.LET):
                return self.parse_declaration()
            raise ParseError(f"Unexpected token {tok.type.name} at line {tok.line}")

    def parse_if(self):
        self.match(TokenType.IF)
        self.match(TokenType.LPAREN)
        cond = self.parse_expression()
        self.match(TokenType.RPAREN)
        self.match(TokenType.LBRACE)
        then_b = self.parse_block()
        else_b = None
        if self.current().type == TokenType.ELSE:
            self.advance()
            self.match(TokenType.LBRACE)
            else_b = self.parse_block()
        return IfStatement(cond, then_b, else_b)

    def parse_while(self):
        self.match(TokenType.WHILE)
        self.match(TokenType.LPAREN)
        cond = self.parse_expression()
        self.match(TokenType.RPAREN)
        self.match(TokenType.LBRACE)
        body = self.parse_block()
        return WhileStatement(cond, body)

    def parse_for(self):
        self.match(TokenType.FOR)
        self.match(TokenType.LPAREN)
        init = self.parse_declaration() # includes the semicolon
        cond = self.parse_expression()
        self.match(TokenType.SEMICOLON)
        
        # update is typically an assignment or increment
        tok = self.current()
        if tok.type in (TokenType.INC, TokenType.DEC):
            op = self.advance().type
            name = self.match(TokenType.IDENTIFIER).value
            sign = "+" if op == TokenType.INC else "-"
            update = Assignment(name, BinOp(Identifier(name), sign, Literal(1, 'int')))
        else:
            name = self.match(TokenType.IDENTIFIER).value
            if self.current().type == TokenType.INC:
                self.advance()
                update = Assignment(name, BinOp(Identifier(name), "+", Literal(1, 'int')))
            elif self.current().type == TokenType.DEC:
                self.advance()
                update = Assignment(name, BinOp(Identifier(name), "-", Literal(1, 'int')))
            else:
                self.match(TokenType.ASSIGN)
                expr = self.parse_expression()
                update = Assignment(name, expr)
        
        self.match(TokenType.RPAREN)
        self.match(TokenType.LBRACE)
        body = self.parse_block()
        return ForStatement(init, cond, update, body)

    def parse_print(self):
        self.match(TokenType.PRINT)
        self.match(TokenType.LPAREN)
        expr = self.parse_expression()
        self.match(TokenType.RPAREN)
        self.match(TokenType.SEMICOLON)
        return PrintStatement(expr)

    def parse_return(self):
        self.match(TokenType.RETURN)
        expr = self.parse_expression()
        self.match(TokenType.SEMICOLON)
        return ReturnStatement(expr)

    # Expression parsing (Pratt/Recursive Descent for precedence)
    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        expr = self.parse_relational()
        while self.current().type in (TokenType.EQ, TokenType.NEQ):
            op = self.advance()
            right = self.parse_relational()
            expr = BinOp(expr, op.value, right)
        return expr

    def parse_relational(self):
        expr = self.parse_term()
        while self.current().type in (TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance()
            right = self.parse_term()
            expr = BinOp(expr, op.value, right)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_factor()
            expr = BinOp(expr, op.value, right)
        return expr

    def parse_factor(self):
        expr = self.parse_primary()
        while self.current().type in (TokenType.MUL, TokenType.DIV):
            op = self.advance()
            right = self.parse_primary()
            expr = BinOp(expr, op.value, right)
        return expr

    def parse_primary(self):
        tok = self.current()
        if tok.type == TokenType.INTEGER_LIT:
            self.advance()
            return Literal(int(tok.value), 'int')
        elif tok.type == TokenType.FLOAT_LIT:
            self.advance()
            return Literal(float(tok.value), 'float')
        elif tok.type == TokenType.STRING_LIT:
            self.advance()
            return Literal(tok.value, 'string')
        elif tok.type == TokenType.IDENTIFIER:
            # Check for function call
            if self.peek().type == TokenType.LPAREN:
                name = self.advance().value
                self.match(TokenType.LPAREN)
                args = []
                if self.current().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    while self.current().type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse_expression())
                self.match(TokenType.RPAREN)
                return FuncCall(name, args)
            else:
                self.advance()
                return Identifier(tok.value)
        elif tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.match(TokenType.RPAREN)
            return expr
        
        raise ParseError(f"Expected expression at line {tok.line}, got {tok.type.name}")

