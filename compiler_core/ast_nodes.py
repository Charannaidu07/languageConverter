class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return "Program"

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return "Block"

class VarDecl(ASTNode):
    def __init__(self, var_type, name, init=None):
        self.var_type = var_type
        self.name = name
        self.init = init
    def __repr__(self): return f"VarDecl({self.var_type}, {self.name})"

class FunctionDecl(ASTNode):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params  # list of (type, name)
        self.body = body # Block
    def __repr__(self): return f"FuncDecl({self.return_type}, {self.name})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self): return "IfStmt"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self): return "WhileStmt"

class ForStatement(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    def __repr__(self): return "ForStmt"

class PrintStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self): return "PrintStmt"

class ReturnStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self): return "ReturnStmt"

class Assignment(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def __repr__(self): return f"Assign({self.name})"

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"BinOp({self.op})"

class Literal(ASTNode):
    def __init__(self, value, val_type):
        self.value = value
        self.val_type = val_type
    def __repr__(self): return f"Literal({self.value})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self): return f"Id({self.name})"

class FuncCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self): return f"Call({self.name})"
