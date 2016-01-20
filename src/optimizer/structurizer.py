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

class Root:
    def __init__(self):
        self.processed = False

class ControlFlowBlock(Root):
    def __init__(self, parent):
        Root.__init__(self)
        self.true_block = None
        self.false_block = None
        self.cmp_inst = None
        self.nested = None
        self.parent = parent

    def __str__(self):
        s = "True: %s <--> False: %s" % (self.true_block, self.false_block)
        return s

class Nested(Root):
    def __init__(self, bb, parent, next=None):
        Root.__init__(self)
        self.bb = bb
        self.next = next
        self.parent = parent

    def __str__(self):
        s = "Nested: %s" % self.bb
        return s

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

    @verify(node=Function)
    def run_on_function(self, node):
        draw_header("Structurizer: %s" % node.name)
        func = node

        queue = Queue()
        queue.put(Nested(func.entry_block, None))

        visited = []
        while not queue.empty():
            nested_bb = queue.get()
            bb = nested_bb.bb

            process = True
            if bb in visited and not nested_bb.processed:
                # Then we have found a terminating condition.
                # Find the root off this control flow block
                while not isinstance(nested_bb, ControlFlowBlock):
                    child = nested_bb
                    nested_bb.processed = True

                    if isinstance(nested_bb.parent, ControlFlowBlock) and \
                    nested_bb.parent.processed is True:
                        nested_bb = nested_bb.parent.parent
                    else:
                        nested_bb = nested_bb.parent

                cfb = nested_bb

                # Now lets look at which side of the cfb we are on.
                if cfb.true_block == child:
                    nested_bb = cfb.false_block
                else:
                    nested_bb = cfb.true_block

                while nested_bb.bb != bb:
                    nested_bb = nested_bb.next

                # Now we found the Basic Block on the other end. This is the convergence point for the true-false block
                # so erase all the children of this node.
                nested_bb.next = None
                process = False
                cfb.processed = True

            visited.append(bb)

            if process:
                terminator = bb.get_terminator()
                if isinstance(terminator, ConditionalBranchInstruction):
                    # Start a visited stack
                    # Start with an If-else block
                    cfb = ControlFlowBlock(nested_bb)
                    cfb.true_block = Nested(terminator.bb_true, cfb)
                    cfb.false_block = Nested(terminator.bb_false, cfb)
                    self.control_flow_stack.append(cfb)

                    queue.put(cfb.true_block)
                    queue.put(cfb.false_block)
                elif isinstance(terminator, BranchInstruction):
                    # Find the branch where it terminates to
                    branch_to_bb = terminator.basic_block
                    nested_bb.next = Nested(branch_to_bb, nested_bb)
                    queue.put(nested_bb.next)
                else:
                    assert isinstance(terminator, ReturnInstruction)