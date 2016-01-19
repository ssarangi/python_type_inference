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

from queue import Queue

class ControlFlowBlock:
    def __init__(self):
        self.true_block = None
        self.false_block = None
        self.cmp_inst = None
        self.nested = None

class Nested:
    def __init__(self, bb, next=None):
        self.bb = bb
        self.next = next

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
        self.control_flow_stack = []

    def get_current_visited_stack(self):
        return self.visited_stack[-1]

    def are_all_blocks_visited(self, func):
        visited_stack = self.get_current_visited_stack()

        for bb in func.basic_blocks:
            if bb not in visited_stack:
                return False

        return True

    @verify(node=Function)
    def run_on_function(self, node):
        draw_header("Structurizer: %s" % node.name)
        func = node

        queue = Queue()
        queue.put(Nested(func.entry_block))


        visited = []
        while not queue.empty():
            nested_bb = queue.get()
            bb = nested_bb.bb

            if bb in visited:
                # Then we have found a terminating condition.
                pass

            terminator = bb.get_terminator()
            if isinstance(terminator, ConditionalBranchInstruction):
                # Start a visited stack
                # Start with an If-else block
                cfb = ControlFlowBlock()
                cfb.true_block = Nested(terminator.bb_true)
                cfb.false_block = Nested(terminator.bb_false)

                queue.put(Nested(terminator.bb_true))
                queue.put(Nested(terminator.bb_false))
            else:
                assert isinstance(terminator, BranchInstruction)
                # Find the branch where it terminates to
                branch_to_bb = terminator.basic_block
                nested_bb.next = Nested(branch_to_bb)