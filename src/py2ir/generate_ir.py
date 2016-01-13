"""
The MIT License (MIT)

Copyright (c) <2015> <sarangis>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from src.ir.module import Module
from src.ir.context import Context
from src.ir.irbuilder import IRBuilder
from src.ir.value import Argument
from src.ir.instructions import CompareTypes

import ast

class IRGenerator(ast.NodeVisitor):
    """
    Constant Propagation Visitor: This class does constant propagation for the node visitor so that types can be inferred
    """
    def __init__(self):
        self.module = None
        self.irbuilder = None
        self.current_scope_stack = []
        self.symbol_tables = [{}]
        self.global_scope = {}
        self.current_func = None

    def get_current_symbol_table(self):
        return self.symbol_tables[-1]

    def current_scope(self):
        return self.current_scope_stack[-1]

    def visit_Module(self, node):
        ctx = Context()
        self.module = Module("root_module", ctx)
        self.irbuilder = IRBuilder(self.module, ctx)

        for expr in node.body:
            ast.NodeVisitor.visit(self, expr)

    def visit_Num(self, node):
        number = self.irbuilder.create_number(node.n)
        return number

    def visit_Str(self, node):
        string = self.irbuilder.create_string(node.s)
        return string

    def visit_Name(self, node):
        name = node.id
        # Find the name in the symbol table
        if name in self.get_current_symbol_table():
            return self.get_current_symbol_table()[name]

        raise Exception("Variable %s not found" % name)

    def visit_BinOp(self, node):
        irbuilder = self.irbuilder
        left = node.left
        right = node.right
        op = node.op
        irleft = ast.NodeVisitor.visit(self, left)
        irright = ast.NodeVisitor.visit(self, right)

        inst = None

        if isinstance(op, ast.Add):
            inst = irbuilder.create_add(irleft, irright, "add")
        elif isinstance(op, ast.Sub):
            inst = irbuilder.create_sub(irleft, irright, "sub")
        elif isinstance(op, ast.Mult):
            inst = irbuilder.create_mul(irleft, irright, "mult")
        elif isinstance(op, ast.Div):
            inst = irbuilder.create_div(irleft, irright, "div")
        elif isinstance(op, ast.LShift):
            inst = irbuilder.create_shl(irleft, irright, "shl")
        elif isinstance(op, ast.RShift):
            inst = irbuilder.create_lshr(irleft, irright, "lshr")

        if inst is None:
            raise Exception("Inst cannot be None")

        return inst

    def visit_Expr(self, node):
        ast.NodeVisitor.visit(self, node.value)


    def visit_Assign(self, node):
        targets = node.targets

        if len(targets) > 1:
            raise Exception("Do not handle more than one return value")

        value = node.value
        rhs = ast.NodeVisitor.visit(self, value)

        target = targets[0]
        self.get_current_symbol_table()[target.id] = rhs

    def visit_Return(self, node):
        value = node.value
        irbuilder = self.irbuilder
        if isinstance(value, ast.Name):
            inst = self.get_current_symbol_table()[value.id]
            irbuilder.create_return(inst)
        else:
            inst = ast.NodeVisitor.visit(self, value)
            irbuilder.create_return(inst)

        self.symbol_tables.pop()

    def visit_GT(self):
        return CompareTypes.SGT

    def visit_GE(self):
        return CompareTypes.SGE

    def visit_EQ(self):
        return CompareTypes.EQ

    def visit_LE(self):
        return CompareTypes.SLE

    def visit_LT(self):
        return CompareTypes.SLT

    def visit_Compare(self, node):
        induction_var = node.left

        assert len(node.comparators) == 1
        induction_var_value_check = node.comparators[0]

        assert len(node.ops) == 1

        # So create a compare instruction
        irbuilder = self.irbuilder
        cmp = irbuilder.create_icmp(self.visit(induction_var), self.visit(induction_var_value_check), self.visit(node.ops[0]))
        return cmp

    def visit_If(self, node):
        cmp = self.visit(node.test)

        irbuilder = self.irbuilder
        if_block = irbuilder.create_basic_block("if", self.current_func)
        else_block = irbuilder.create_basic_block("else", self.current_func)
        exit_if_block = irbuilder.create_basic_block("endif", self.current_func)

        irbuilder.create_cond_branch(cmp, 1, if_block, else_block)

        # Add the code for the if-block
        irbuilder.insert_after(if_block)
        for inst in node.body:
            self.visit(inst)

        if not if_block.has_terminator():
            irbuilder.create_branch(exit_if_block)

        # Add the code for the else-block
        irbuilder.insert_after(else_block)
        for inst in node.orelse:
            self.visit(inst)

        if not else_block.has_terminator():
            irbuilder.create_branch(exit_if_block)

    def visit_Call(self, node):
        irbuilder = self.irbuilder
        irfunc = self.global_scope[node.func.id]

        args = node.args

        irargs = []
        for arg in args:
            if isinstance(arg, ast.Name):
                irarg = self.get_current_symbol_table()[arg.name]
            else:
                irarg = ast.NodeVisitor.visit(self, arg)

            irargs.append(irarg)

        inst = irbuilder.create_call(irfunc, irargs)
        return inst

    def visit_FunctionDef(self, func):
        irbuilder = self.irbuilder
        self.symbol_tables.append({})
        irargs = [Argument(arg.arg) for arg in func.args.args]

        for irarg in irargs:
            self.get_current_symbol_table()[irarg.name] = irarg

        irfunc = irbuilder.create_function(func.name, irargs)
        self.current_func = irfunc

        entry_bb = irbuilder.create_basic_block("entry", irfunc)
        irfunc.basic_blocks.append(entry_bb)
        irbuilder.insert_after(entry_bb)

        for inst in func.body:
            ast.NodeVisitor.visit(self, inst)

        self.global_scope[func.name] = irfunc

        if func.name == "main":
            self.module.entry_point = irfunc

