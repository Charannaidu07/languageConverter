from .ast_nodes import *
from .ir import *

class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"IR Gen: No visit_{type(node).__name__} method")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.generate(stmt)
        return self.instructions

    def visit_Block(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    def visit_VarDecl(self, node):
        if node.init:
            val = self.generate(node.init)
            self.emit(TACAssign(node.name, None, val))

    def visit_FunctionDecl(self, node):
        self.emit(TACLabel(node.name))
        for p_type, p_name in node.params:
            self.emit(TACAssign(p_name, None, f"arg_{p_name}")) # Simplified param handling
        self.generate(node.body)

    def visit_IfStatement(self, node):
        cond_val = self.generate(node.condition)
        false_label = self.new_label()
        end_label = self.new_label()

        self.emit(TACIfFalseGoto(cond_val, false_label))
        self.generate(node.then_branch)
        self.emit(TACGoto(end_label))
        self.emit(TACLabel(false_label))
        
        if node.else_branch:
            self.generate(node.else_branch)
            
        self.emit(TACLabel(end_label))

    def visit_WhileStatement(self, node):
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(TACLabel(start_label))
        cond_val = self.generate(node.condition)
        self.emit(TACIfFalseGoto(cond_val, end_label))
        
        self.generate(node.body)
        self.emit(TACGoto(start_label))
        self.emit(TACLabel(end_label))

    def visit_ForStatement(self, node):
        self.generate(node.init)
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(TACLabel(start_label))
        cond_val = self.generate(node.condition)
        self.emit(TACIfFalseGoto(cond_val, end_label))
        
        self.generate(node.body)
        self.generate(node.update)
        self.emit(TACGoto(start_label))
        self.emit(TACLabel(end_label))

    def visit_PrintStatement(self, node):
        val = self.generate(node.expr)
        self.emit(TACParam(val))
        self.emit(TACCall("print", 1))

    def visit_ReturnStatement(self, node):
        val = self.generate(node.expr)
        self.emit(TACReturn(val))

    def visit_Assignment(self, node):
        val = self.generate(node.expr)
        self.emit(TACAssign(node.name, None, val))
        return node.name

    def visit_BinOp(self, node):
        left_val = self.generate(node.left)
        right_val = self.generate(node.right)
        temp = self.new_temp()
        self.emit(TACAssign(temp, node.op, left_val, right_val))
        return temp

    def visit_Literal(self, node):
        return str(node.value)

    def visit_Identifier(self, node):
        return node.name

    def visit_FuncCall(self, node):
        args = [self.generate(arg) for arg in node.args]
        for arg in args:
            self.emit(TACParam(arg))
        temp = self.new_temp()
        self.emit(TACCall(node.name, len(args), temp))
        return temp
