"""
The MIT License (MIT)

Copyright (c) 2015 <Satyajit Sarangi>

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

from src.ir.function import *
from src.ir.constants import Number
from src.ir.base_ir_visitor import IRBaseVisitor
from src.optimizer.pass_support import *
from src.utils.print_utils import draw_header

BINARY_OPERATORS = {
    '+':   lambda x, y: x + y,
    '-':   lambda x, y: x - y,
    '*':   lambda x, y: x * y,
    '**':  lambda x, y: x ** y,
    '/':   lambda x, y: x / y,
    '//':  lambda x, y: x // y,
    '<<':  lambda x, y: x << y,
    '>>':  lambda x, y: x >> y,
    '%':   lambda x, y: x % type(x)(y),
    '&':   lambda x, y: x & y,
    '|':   lambda x, y: x | y,
    '^':   lambda x, y: x ^ y,
}

class ConstPropagationPass(FunctionPass, IRBaseVisitor):
    def __init__(self):
        FunctionPass.__init__(self)
        IRBaseVisitor.__init__(self)
        self.insts_to_remove = []

    @verify(node=Function)
    def run_on_function(self, node):
        draw_header("Constant Propagation: %s" % node.name)
        func = node

        for bb in func.basic_blocks:
            self.visit_basicblock(bb)

        print(node)

    def visit_basicblock(self, node):
        for inst in node.instructions:
            IRBaseVisitor.visit(self, inst)

        for inst in self.insts_to_remove:
            inst.erase_from_parent()

        self.insts_to_remove.clear()

    def const_fold_binary_op(self, lhs, rhs, op):
        result = None
        if isinstance(lhs, Number) and isinstance(rhs, Number):
            result = BINARY_OPERATORS[op](lhs.number, rhs.number)
            result = Number(result)

        return result

    def replace_uses_with_const(self, node, const):
        for use in node.uses:
            self.replace_use_with_const(node, use, const)

        self.insts_to_remove.append(node)

    def replace_use_with_const(self, node,  use, const):
        if hasattr(use, "operands"):
            for i, ops in enumerate(use.operands):
                if ops == node:
                    use.operands[i] = const

    def visit_returninstruction(self, node):
        pass

    def visit_addinstruction(self, node):
        lhs = node.lhs
        rhs = node.rhs

        result = self.const_fold_binary_op(lhs, rhs, '+')
        if result is not None:
            self.replace_uses_with_const(node, result)

    def visit_subinstruction(self, node):
        lhs = node.lhs
        rhs = node.rhs

        result = self.const_fold_binary_op(lhs, rhs, '-')
        if result is not None:
            self.replace_uses_with_const(node, result)

    def visit_mulinstruction(self, node):
        lhs = node.lhs
        rhs = node.rhs

        result = self.const_fold_binary_op(lhs, rhs, '*')
        if result is not None:
            self.replace_uses_with_const(node, result)

    def visit_divinstruction(self, node):
        lhs = node.lhs
        rhs = node.rhs

        result = self.const_fold_binary_op(lhs, rhs, '/')
        if result is not None:
            self.replace_uses_with_const(node, result)