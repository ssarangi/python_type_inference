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

from src.ir.function import *
from src.ir.constants import Number
from src.ir.base_ir_visitor import IRBaseVisitor
from src.ir.irbuilder import IRBuilder

from src.optimizer.pass_support import *
from src.utils.print_utils import draw_header

class ConstPropagationPass(FunctionPass, IRBaseVisitor):
    def __init__(self):
        FunctionPass.__init__(self)
        IRBaseVisitor.__init__(self)
        self.insts_to_remove = []
        self.irbuilder = None

    @verify(node=Function)
    def run_on_function(self, node):
        draw_header("Instruction Combining: %s" % node.name)
        func = node

        for bb in func.basic_blocks:
            self.visit_basicblock(bb)

        print(node)