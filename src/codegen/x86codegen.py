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
from src.ir.module import Module
from src.ir.constants import Number, String
from src.ir.base_ir_visitor import IRBaseVisitor
from src.optimizer.pass_support import *
from src.utils.print_utils import draw_header

import src.pyasm2.x86 as x86

class x86CodeGen(ModulePass, IRBaseVisitor):
    def __init__(self):
        ModulePass.__init__(self)
        IRBaseVisitor.__init__(self)
        self.function_block_mapping = []
        self.current_bb = None

    def create_new_assembly_block(self):
        self.current_bb = x86.Block()
        self.function_block_mapping.append(self.current_bb)

    def current_assembly_block(self):
        return self.current_bb

    def get_assembly_bytes(self):
        bytes = None
        for block in self.function_block_mapping:
            bytes = block.assemble()

        return bytes

    @verify(node=Module)
    def run_on_module(self, node):
        draw_header("x86 Code Generation")

        # Generate code for "main"
        if "main" not in node.functions:
            raise Exception("No main function in the IR")

        self.visit(node.functions["main"], [])

    def visit_function(self, node, arglist):
        for bb in node.basic_blocks:
            self.visit(bb)

    def visit_basicblock(self, node):
        # Create a new assembly block
        self.create_new_assembly_block()

        for inst in node.instructions:
            self.visit(inst)

    def visit_returninstruction(self, node):
        asm_block = self.current_assembly_block()
        asm_block.append(x86.ret())

    def visit_addinstruction(self, node):
        pass

    def visit_subinstruction(self, node):
        pass

    def visit_mulinstruction(self, node):
        asm_block = self.current_assembly_block()
        # For now lets handle the immediates
        if isinstance(node.lhs, Number) and isinstance(node.rhs, Number):
            asm_block.append(x86.mov(x86.eax, node.lhs.number))
            asm_block.append(x86.mov(x86.ebx, node.rhs.number))
            asm_block.append(x86.imul(x86.eax, x86.ebx))

    def visit_divinstruction(self, node):
        pass