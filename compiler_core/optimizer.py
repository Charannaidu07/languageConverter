from .ir import *

class Optimizer:
    def __init__(self):
        pass

    def optimize(self, instructions):
        # Pass 1: Constant Folding on assignments
        new_instructions = []
        constants = {} # trace simple constants: temp -> literal
        
        import re
        is_temp = lambda x: bool(re.match(r'^t\d+$', str(x)))
        
        for instr in instructions:
            if isinstance(instr, TACAssign):
                # Check if arg1 and arg2 are constants
                val1 = self._get_literal(instr.arg1, constants)
                if instr.arg2:
                    val2 = self._get_literal(instr.arg2, constants)
                    if val1 is not None and val2 is not None:
                        # Perform fold
                        try:
                            # Safely eval math on constants
                            folded = eval(f"{val1} {instr.op} {val2}")
                            if isinstance(folded, bool):
                                folded = "true" if folded else "false"
                            # Keep it generic
                            new_instructions.append(TACAssign(instr.target, None, str(folded)))
                            if is_temp(instr.target):
                                constants[instr.target] = str(folded)
                            continue
                        except:
                            pass
                elif val1 is not None:
                    # Direct assignment of constant
                    if is_temp(instr.target):
                        constants[instr.target] = val1
            new_instructions.append(instr)
            
        return new_instructions

    def _get_literal(self, arg, constants):
        if arg in constants:
            return constants[arg]
        # Check if arg is numeric string
        try:
            float(arg)
            return arg
        except ValueError:
            return None
