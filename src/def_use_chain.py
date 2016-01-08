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

import ast

class DefUseChain(ast.NodeVisitor):
    def __init__(self):
        self.current_scope_stack = []

    def current_scope(self):
        return self.current_scope_stack[-1]

    def visit_Module(self, node):
        self.current_scope_stack.append(node)

        for expr in node.body:
            ast.NodeVisitor.visit(self, expr)

    def visit_Name(self, node):
        if hasattr(node, "uses"):
            node.uses.append(node.parent)
        else:
            node.uses = [node.parent]

    def visit_BinOp(self, node):
        node.left.parent = node
        node.right.parent = node
        ast.NodeVisitor.visit(self, node.left)
        ast.NodeVisitor.visit(self, node.right)

    def visit_Expr(self, node):
        ast.NodeVisitor.visit(self, node.value)

    def visit_Assign(self, node):
        targets = node.targets

        for target in targets:
            target.parent = node
            ast.NodeVisitor.visit(self, target)

        node.value.parent = node
        ast.NodeVisitor.visit(self, node.value)

    def visit_Str(self, node):
        node.parent = self.current_scope()

    def visit_Return(self, node):
        node.value.parent = node
        ast.NodeVisitor.visit(self, node.value)
        self.current_scope_stack.pop()

    def visit_Call(self, node):
        node.parent = self.current_scope()

        if hasattr(node.func, "uses"):
            node.func.uses.append(node)
        else:
            node.func.uses = [node]

    def visit_FunctionDef(self, func):
        self.current_scope_stack.append(func)

        func.locals = []

        for arg in func.args.args:
            arg.uses = []
            func.locals.append(arg.arg)

        for inst in func.body:
            ast.NodeVisitor.visit(self, inst)