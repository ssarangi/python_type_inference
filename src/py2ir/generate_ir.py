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

import ast

class IRGenerator(ast.NodeVisitor):
    """
    Constant Propagation Visitor: This class does constant propagation for the node visitor so that types can be inferred
    """
    def __init__(self):
        self.module = None
        self.irbuilder = None
        self.current_scope_stack = []
        self.symbol_table = {}

    def current_scope(self):
        return self.current_scope_stack[-1]

    def visit_Module(self, node):
        print(ast.dump(node))
        ctx = Context()
        self.module = Module("root_module", ctx)
        self.irbuilder = IRBuilder(self.module, ctx)

        for expr in node.body:
            ast.NodeVisitor.visit(self, expr)

    def visit_Name(self, node):
        pass

    def visit_BinOp(self, node):
        pass

    def visit_Expr(self, node):
        ast.NodeVisitor.visit(self, node.value)


    def visit_Assign(self, node):
        targets = node.targets
        value = node.value
        pass


    def visit_Str(self, node):
        pass

    def visit_Return(self, node):
        pass

    def visit_Call(self, node):
        pass

    def visit_FunctionDef(self, func):
        args = [Argument(arg.arg) for arg in func.args.args]
        irfunc = self.irbuilder.create_function(func.name, func.args.args)
        self.module.functions.append(irfunc)

        for inst in func.body:
            ast.NodeVisitor.visit(self, inst)