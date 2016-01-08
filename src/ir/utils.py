__author__ = 'sarangis'

import ir.instructions
from ir.constants import *

def is_terminator_instruction(inst):
    if (isinstance(inst, ir.instructions.TerminateInstruction) or
        isinstance(inst, ir.instructions.ReturnInstruction) or
        isinstance(inst, ir.instructions.BranchInstruction) or
        isinstance(inst, ir.instructions.ConditionalBranchInstruction)):
        return True
    else:
        return False

def render_list_with_parens(custom_list):
    output_str = "("
    for idx, i in enumerate(custom_list):
        if hasattr(i, "name"):
            output_str += i.name
        else:
            output_str += str(i)

        if idx < len(custom_list) - 1:
            output_str += ", "

    output_str += ")"

    return output_str