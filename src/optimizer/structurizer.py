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
from src.ir.instructions import *
from src.ir.base_ir_visitor import IRBaseVisitor
from src.optimizer.pass_support import *
from src.utils.print_utils import draw_header

class IfElseBlock:
    def __init__(self):
        self.true_block = None
        self.false_block = None
        self.cmp_inst = None


def find_culminating_block(start_bb):
    while not start_bb.is_empty() and start_bb.has_terminator():
        terminator = start_bb.get_terminator()
        if isinstance(terminator, BranchInstruction):
            start_bb = terminator.basic_block
        else:
            return start_bb

class StructurizerAnalysisPass(FunctionPass, IRBaseVisitor):
    def __init__(self):
        FunctionPass.__init__(self)
        IRBaseVisitor.__init__(self)

        self.structurizable_blocks = None
        self.func_to_structurizable_blocks = {}

    @verify(node=Function)
    def run_on_function(self, node):
        structurizable_blocks = {}
        self.func_to_structurizable_blocks[node.name] = structurizable_blocks
        draw_header("Structurizer: %s" % node.name)
        func = node

        for bb in func.basic_blocks:
            if bb in structurizable_blocks.keys():
                continue

            # Check to see if the bb has a terminator block
            if bb.has_terminator():
                terminator = bb.get_terminator()
                if isinstance(terminator, ConditionalBranchInstruction):
                    # Ok this might be the if condition.
                    true_block = terminator.bb_true
                    false_block = terminator.bb_false

                    # Find the culminating block for the BB
                    true_block_culminator = find_culminating_block(true_block)
                    false_block_culminator = find_culminating_block(false_block)

                    if true_block_culminator == false_block_culminator:
                        # For now we can assume that this is an if block.
                        ifelseblock = IfElseBlock()
                        ifelseblock.true_block = true_block
                        ifelseblock.false_block = false_block

                        # Now figure out the induction variable
                        ifelseblock.cmp_inst = terminator.cmp_inst

                        structurizable_blocks[node] = ifelseblock

