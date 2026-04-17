from .ast_nodes import *

class CodeGenerator:
    def __init__(self, target_lang):
        self.target_lang = target_lang

    def generate(self, node):
        # We start by generating the inner content and then wrap it based on language.
        inner_code = self._gen(node, 1 if self.target_lang != "python" else 0)
        if self.target_lang == "java":
            return f"public class Main {{\n    public static void main(String[] args) {{\n{inner_code}    }}\n}}"
        elif self.target_lang == "c":
            return f"#include <stdio.h>\n\nint main() {{\n{inner_code}    return 0;\n}}"
        elif self.target_lang == "cpp":
            return f"#include <iostream>\nusing namespace std;\n\nint main() {{\n{inner_code}    return 0;\n}}"
        elif self.target_lang == "minilang":
            return f"def main() {{\n{inner_code}}}"
        elif self.target_lang == "python":
            return f"def main():\n{self._gen(node, 1)}\n\nif __name__ == '__main__':\n    main()\n"
        return inner_code

    def ind(self, level):
        return "    " * level

    def _gen(self, node, level=0):
        if node is None:
            return ""
        method_name = f'gen_{type(node).__name__}'
        generator = getattr(self, method_name, self.generic_gen)
        return generator(node, level)

    def generic_gen(self, node, level):
        return f"{self.ind(level)}// Unhandled node: {type(node).__name__}\n"

    def gen_Program(self, node, level):
        code = ""
        for stmt in node.statements:
            code += self._gen(stmt, level)
        return code

    def gen_Block(self, node, level):
        code = ""
        for stmt in node.statements:
            code += self._gen(stmt, level)
        return code

    def gen_FunctionDecl(self, node, level):
        if node.name in ("main", "Main"):
            # Main is automatically wrapped by our top level generate() function
            # So we just seamlessly strip the original wrapper and splice the pure body!
            return self._gen(node.body, level)

        # For user defined functions
        ret = node.return_type
        if self.target_lang == "minilang":
            ret = "def"
        elif self.target_lang == "java":
            ret = f"public static {ret}" # Java needs static members since we wrap inside a main class
            
        param_arr = []
        for pt, pn in node.params:
            if self.target_lang == "minilang":
                 param_arr.append(pn)
            elif self.target_lang == "python":
                 param_arr.append(pn)
            else:
                 p_type = pt if pt != 'auto' else 'int'
                 param_arr.append(f"{p_type} {pn}")
                 
        params = ", ".join(param_arr)
        body = self._gen(node.body, level + 1)
        if self.target_lang == "python":
            return f"{self.ind(level)}def {node.name}({params}):\n{body}\n"
        return f"{self.ind(level)}{ret} {node.name}({params}) {{\n{body}{self.ind(level)}}}\n"

    def gen_VarDecl(self, node, level):
        v_type = node.var_type
        if self.target_lang == "minilang":
            decl = f"let {node.name}"
        elif self.target_lang == "python":
            decl = f"{node.name}"
        else:
            if v_type == 'auto':
                v_type = "auto" if self.target_lang == "cpp" else "int" # fallback
            decl = f"{v_type} {node.name}"
            
        if node.init:
            return f"{self.ind(level)}{decl} = {self._gen_expr(node.init)}\n" if self.target_lang == "python" else f"{self.ind(level)}{decl} = {self._gen_expr(node.init)};\n"
        return f"{self.ind(level)}{decl} = None\n" if self.target_lang == "python" else f"{self.ind(level)}{decl};\n"

    def gen_Assignment(self, node, level):
        return f"{self.ind(level)}{node.name} = {self._gen_expr(node.expr)}\n" if self.target_lang == "python" else f"{self.ind(level)}{node.name} = {self._gen_expr(node.expr)};\n"

    def gen_IfStatement(self, node, level):
        cond = self._gen_expr(node.condition)
        if self.target_lang == "python":
            code = f"{self.ind(level)}if {cond}:\n{self._gen(node.then_branch, level+1)}"
            if node.else_branch:
                code += f"{self.ind(level)}else:\n{self._gen(node.else_branch, level+1)}"
            return code
        
        code = f"{self.ind(level)}if ({cond}) {{\n{self._gen(node.then_branch, level+1)}{self.ind(level)}}}\n"
        if node.else_branch:
            code += f"{self.ind(level)}else {{\n{self._gen(node.else_branch, level+1)}{self.ind(level)}}}\n"
        return code

    def gen_WhileStatement(self, node, level):
        cond = self._gen_expr(node.condition)
        if self.target_lang == "python":
            return f"{self.ind(level)}while {cond}:\n{self._gen(node.body, level+1)}"
        return f"{self.ind(level)}while ({cond}) {{\n{self._gen(node.body, level+1)}{self.ind(level)}}}\n"
        
    def gen_ForStatement(self, node, level):
        if self.target_lang == "python":
            init = self._gen(node.init, level)
            cond = self._gen_expr(node.condition)
            update = self._gen(node.update, level+1)
            body = self._gen(node.body, level+1)
            return f"{init}{self.ind(level)}while {cond}:\n{body}{update}"
        else:
            init = self._gen(node.init, 0).strip()
            cond = self._gen_expr(node.condition)
            update = self._gen(node.update, 0).strip().replace(';', '')
            return f"{self.ind(level)}for ({init} {cond}; {update}) {{\n{self._gen(node.body, level+1)}{self.ind(level)}}}\n"

    def gen_PrintStatement(self, node, level):
        expr = self._gen_expr(node.expr)
        if self.target_lang == "c":
            if '"' in expr: # simple string check
                return f'{self.ind(level)}printf("%s\\n", {expr});\n'
            return f'{self.ind(level)}printf("%d\\n", {expr});\n'
        elif self.target_lang == "cpp":
            return f'{self.ind(level)}cout << {expr} << endl;\n'
        elif self.target_lang == "java":
            return f'{self.ind(level)}System.out.println({expr});\n'
        elif self.target_lang == "python":
            return f'{self.ind(level)}print({expr})\n'
        else:
            return f'{self.ind(level)}print({expr});\n'

    def gen_ReturnStatement(self, node, level):
        if (self.target_lang in ("java", "c", "cpp")) and isinstance(node.expr, Literal) and node.expr.value == 0:
            return ""
        return f"{self.ind(level)}return {self._gen_expr(node.expr)}\n" if self.target_lang == "python" else f"{self.ind(level)}return {self._gen_expr(node.expr)};\n"

    def gen_FuncCall(self, node, level):
        if node.name in ("print", "printf", "printJava", "printCpp"):
            if len(node.args) > 1:
                expr = node.args[-1]
            elif len(node.args) == 1:
                expr = node.args[0]
            else:
                expr = Literal('""', 'string')
            return self.gen_PrintStatement(PrintStatement(expr), level)
        return f"{self.ind(level)}{node.name}({', '.join(self._gen_expr(a) for a in node.args)})\n" if self.target_lang == "python" else f"{self.ind(level)}{node.name}({', '.join(self._gen_expr(a) for a in node.args)});\n"

    # Expression parsing below
    def _gen_expr(self, node):
        if isinstance(node, BinOp):
            return f"{self._gen_expr(node.left)} {node.op} {self._gen_expr(node.right)}"
        elif isinstance(node, Literal):
            if node.val_type == 'string':
                return f'"{node.value}"'
            return str(node.value)
        elif isinstance(node, Identifier):
            return node.name
        elif isinstance(node, FuncCall):
            return f"{node.name}({', '.join(self._gen_expr(a) for a in node.args)})"
        return ""
