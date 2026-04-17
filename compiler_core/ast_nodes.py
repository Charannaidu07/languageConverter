class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return f"Program({self.statements!r})"

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return f"Block({self.statements!r})"

class VarDecl(ASTNode):
    def __init__(self, var_type, name, init=None):
        self.var_type = var_type
        self.name = name
        self.init = init
    def __repr__(self): return f"VarDecl({self.var_type!r}, {self.name!r}, {self.init!r})"

class FunctionDecl(ASTNode):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params  # list of (type, name)
        self.body = body # Block
    def __repr__(self): return f"FunctionDecl({self.return_type!r}, {self.name!r}, {self.params!r}, {self.body!r})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self): return f"IfStatement({self.condition!r}, {self.then_branch!r}, {self.else_branch!r})"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self): return f"WhileStatement({self.condition!r}, {self.body!r})"

class ForStatement(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    def __repr__(self): return f"ForStatement({self.init!r}, {self.condition!r}, {self.update!r}, {self.body!r})"

class PrintStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self): return f"PrintStatement({self.expr!r})"

class ReturnStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self): return f"ReturnStatement({self.expr!r})"

class Assignment(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def __repr__(self): return f"Assignment({self.name!r}, {self.expr!r})"

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"BinOp({self.left!r}, {self.op!r}, {self.right!r})"

class Literal(ASTNode):
    def __init__(self, value, val_type):
        self.value = value
        self.val_type = val_type
    def __repr__(self): return f"Literal({self.value!r}, {self.val_type!r})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self): return f"Identifier({self.name!r})"

class FuncCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self): return f"FuncCall({self.name!r}, {self.args!r})"
