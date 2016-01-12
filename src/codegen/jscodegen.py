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
from src.ir.module import Module
from src.ir.constants import Number, String
from src.ir.base_ir_visitor import IRBaseVisitor
from src.optimizer.pass_support import *
from src.utils.print_utils import draw_header
from src.codegen.jscode import EmitJS

class JSFunction:
    def __init__(self, name):
        self.name = name
        self.code = []

    def append(self, inst):
        self.code.append(inst)

    def __str__(self):
        # Generate the function name
        js_str = "var %s = function() {\n" % self.name
        js_str += "\n".join(self.code)
        js_str += "\n}"
        return js_str

    __repr__ = __str__

class JSCodeGen(ModulePass, IRBaseVisitor):
    def __init__(self):
        ModulePass.__init__(self)
        IRBaseVisitor.__init__(self)
        self.function_block_mapping = []
        self.current_bb = None
        self.function_code = {}
        self.fn_stack = []
        self.emit = EmitJS()

    def current_fn(self):
        return self.fn_stack[-1]

    def get_code(self):
        js_code = ""
        for name, fn in self.function_code.items():
            js_code += str(fn)

        # Run the main function()
        js_code += "\nconsole.log(main());"
        return js_code

    @verify(node=Module)
    def run_on_module(self, node):
        draw_header("Javascript Code Generation")

        # Generate code for "main"
        if "main" not in node.functions:
            raise Exception("No main function in the IR")

        self.visit(node.functions["main"], [])

    def visit_function(self, node, arglist):
        self.emit.indent()
        fn = JSFunction(node.name)
        self.function_code[node.name] = fn
        self.fn_stack.append(fn)

        for bb in node.basic_blocks:
            self.visit(bb)

    def visit_basicblock(self, node):
        # Create a new assembly block
        for inst in node.instructions:
            self.visit(inst)

    def visit_returninstruction(self, node):
        inst = self.emit.ret(node.value.name)
        self.current_fn().append(inst)

    def visit_addinstruction(self, node):
        pass

    def visit_subinstruction(self, node):
        pass

    def visit_mulinstruction(self, node):
        inst = self.emit.binary_inst(node.lhs, '*', node.rhs, node.name)
        self.current_fn().append(inst)


    def visit_divinstruction(self, node):
        pass
