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
from src.ir.instructions import *

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
        self.cfg_stack = []
        self.current_exit_block = None

    def get_current_symbol_table(self):
        return self.symbol_tables[-1]

    def set_symbol(self, sym, val):
        sym_table = self.get_current_symbol_table()
        sym_table[sym] = val

    def get_symbol(self, sym):
        sym_table = self.get_current_symbol_table()
        if sym in sym_table:
            return sym_table[sym]

        return None

    def in_symbol_table(self, sym):
        sym_table = self.get_current_symbol_table()
        if sym in sym_table:
            return True

        return False

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
        if self.in_symbol_table(name):
            return self.get_symbol(name)

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
        irbuilder = self.irbuilder
        targets = node.targets

        if len(targets) > 1:
            raise Exception("Do not handle more than one return value")

        value = node.value
        rhs = ast.NodeVisitor.visit(self, value)

        target = targets[0]
        target_sym = self.get_symbol(target.id)

        if target_sym is None:
            # Create an alloca for this target symbol
            target_sym = irbuilder.create_alloca(name=target.id)
            self.set_symbol(target.id, target_sym)

        assert isinstance(target_sym, AllocaInstruction)

        if isinstance(rhs, AllocaInstruction):
            rhs = irbuilder.create_load(rhs)

        irbuilder.create_store(target_sym, rhs)

    def visit_Return(self, node):
        value = node.value
        irbuilder = self.irbuilder
        retv_sym = self.get_symbol("retv")

        if isinstance(value, ast.Name):
            inst = self.get_symbol(value.id)

            if isinstance(inst, AllocaInstruction):
                inst = irbuilder.create_load(inst)
            irbuilder.create_store(retv_sym, inst)
        else:
            inst = ast.NodeVisitor.visit(self, value)

            if isinstance(inst, AllocaInstruction):
                inst = irbuilder.create_load(inst)

            irbuilder.create_store(retv_sym, inst)

        irbuilder.create_branch(self.current_exit_block)
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
        if_block = irbuilder.create_basic_block("then", self.current_func)
        else_block = irbuilder.create_basic_block("else", self.current_func)
        exit_if_block = irbuilder.create_basic_block("endif", self.current_func)

        irbuilder.create_cond_branch(cmp, 1, if_block, else_block)

        # Add the code for the if-block
        self.current_func.basic_blocks.append(if_block)
        irbuilder.insert_after(if_block)
        for inst in node.body:
            self.visit(inst)

        current_blk = irbuilder.get_current_bb()
        if not current_blk.has_terminator():
            irbuilder.create_branch(exit_if_block)

        # Add the code for the else-block
        self.current_func.basic_blocks.append(else_block)
        irbuilder.insert_after(else_block)
        for inst in node.orelse:
            self.visit(inst)

        current_blk = irbuilder.get_current_bb()
        if not current_blk.has_terminator():
            irbuilder.create_branch(exit_if_block)

        self.current_func.basic_blocks.append(exit_if_block)
        irbuilder.insert_after(exit_if_block)

    def visit_Call(self, node):
        irbuilder = self.irbuilder
        irfunc = self.global_scope[node.func.id]

        args = node.args

        irargs = []
        for arg in args:
            if isinstance(arg, ast.Name):
                irarg = self.get_symbol(arg.name)
            else:
                irarg = ast.NodeVisitor.visit(self, arg)

            irargs.append(irarg)

        inst = irbuilder.create_call(irfunc, irargs)
        return inst

    def visit_FunctionDef(self, func):
        irbuilder = self.irbuilder
        self.symbol_tables.append({})
        irargs = [Argument(arg.arg) for arg in func.args.args]

        irfunc = irbuilder.create_function(func.name, irargs)
        self.current_func = irfunc

        entry_bb = irbuilder.create_basic_block("entry", irfunc)
        irfunc.basic_blocks.append(entry_bb)
        exit_bb = irbuilder.create_basic_block("exit", irfunc)
        self.current_exit_block = exit_bb

        irbuilder.insert_after(entry_bb)
        # Create an alloca for the return value
        retv = irbuilder.create_alloca(name="retv")
        self.set_symbol("retv", retv)

        # Now create allocas for every argument
        for irarg in irargs:
            alloca = irbuilder.create_alloca()
            irbuilder.create_store(alloca, irarg)
            self.set_symbol(irarg.name, alloca)

        for inst in func.body:
            ast.NodeVisitor.visit(self, inst)

        # Now we should have completed generating all the code. So create
        # the return value
        irfunc.basic_blocks.append(exit_bb)

        irbuilder.insert_after(exit_bb)
        retv_loaded = irbuilder.create_load(retv)
        irbuilder.create_return(retv_loaded)

        self.global_scope[func.name] = irfunc

        if func.name == "main":
            self.module.entry_point = irfunc