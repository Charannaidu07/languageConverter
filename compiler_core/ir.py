class TAC:
    pass

class TACAssign(TAC):
    def __init__(self, target, op, arg1, arg2=None):
        self.target = target
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2 # None for unary assignments like t1 = t2
    def __repr__(self):
        if self.arg2:
            return f"{self.target} = {self.arg1} {self.op} {self.arg2}"
        elif self.op:
            return f"{self.target} = {self.op} {self.arg1}"
        else:
            return f"{self.target} = {self.arg1}"

class TACLabel(TAC):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"{self.name}:"

class TACGoto(TAC):
    def __init__(self, label):
        self.label = label
    def __repr__(self):
        return f"goto {self.label}"

class TACIfGoto(TAC):
    def __init__(self, condition, label):
        self.condition = condition
        self.label = label
    def __repr__(self):
        return f"if {self.condition} goto {self.label}"

class TACIfFalseGoto(TAC):
    def __init__(self, condition, label):
        self.condition = condition
        self.label = label
    def __repr__(self):
        return f"iffalse {self.condition} goto {self.label}"

class TACParam(TAC):
    def __init__(self, arg):
        self.arg = arg
    def __repr__(self):
        return f"param {self.arg}"

class TACCall(TAC):
    def __init__(self, func, num_args, target=None):
        self.func = func
        self.num_args = num_args
        self.target = target
    def __repr__(self):
        if self.target:
            return f"{self.target} = call {self.func}, {self.num_args}"
        return f"call {self.func}, {self.num_args}"

class TACReturn(TAC):
    def __init__(self, arg=None):
        self.arg = arg
    def __repr__(self):
        if self.arg:
            return f"return {self.arg}"
        return "return"
