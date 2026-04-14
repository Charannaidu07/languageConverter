from .ast_nodes import *

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        # Pre-seed with basic global built-ins
        self.symbol_table = [{'print': 'func', 'printf': 'func', 'printJava': 'func', 'printCpp': 'func', 'System': 'class', 'cout': 'obj'}]
        self.errors = []

    def enter_scope(self):
        self.symbol_table.append({})

    def exit_scope(self):
        self.symbol_table.pop()

    def declare(self, name, var_type):
        if name in self.symbol_table[-1]:
            self.errors.append(f"Variable '{name}' already declared in this scope.")
        self.symbol_table[-1][name] = var_type

    def resolve(self, name):
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        self.errors.append(f"Undefined variable '{name}'.")
        return None

    def analyze(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.analyze(stmt)
        if self.errors:
            error_msg = "\n".join(self.errors)
            raise SemanticError(f"Semantic analysis failed:\n{error_msg}")

    def visit_Block(self, node):
        self.enter_scope()
        for stmt in node.statements:
            self.analyze(stmt)
        self.exit_scope()

    def visit_VarDecl(self, node):
        if node.init:
            self.analyze(node.init)
        self.declare(node.name, node.var_type)

    def visit_FunctionDecl(self, node):
        self.declare(node.name, "function")
        self.enter_scope()
        for p_type, p_name in node.params:
            self.declare(p_name, p_type)
        self.visit_Block(node.body) # visit the block directly as we already entered scope
        self.exit_scope()

    def visit_IfStatement(self, node):
        self.analyze(node.condition)
        self.analyze(node.then_branch)
        if node.else_branch:
            self.analyze(node.else_branch)

    def visit_WhileStatement(self, node):
        self.analyze(node.condition)
        self.analyze(node.body)

    def visit_ForStatement(self, node):
        self.enter_scope() # For loop has its own scope for init
        self.analyze(node.init)
        self.analyze(node.condition)
        self.analyze(node.update)
        # We don't call self.analyze(node.body) directly if it's a Block, to avoid double scope,
        # actually, Block creates its own scope anyway. That's fine, inner scope.
        self.analyze(node.body)
        self.exit_scope()

    def visit_PrintStatement(self, node):
        self.analyze(node.expr)

    def visit_ReturnStatement(self, node):
        self.analyze(node.expr)

    def visit_Assignment(self, node):
        self.resolve(node.name) # Check if it exists
        self.analyze(node.expr)

    def visit_BinOp(self, node):
        self.analyze(node.left)
        self.analyze(node.right)

    def visit_Literal(self, node):
        pass

    def visit_Identifier(self, node):
        self.resolve(node.name)

    def visit_FuncCall(self, node):
        self.resolve(node.name) # Not doing strict arg length checking for simplicity
        for arg in node.args:
            self.analyze(arg)
