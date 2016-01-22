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
    def __init__(self, parent):
        self.processed = False
        self.__parent = parent
        self.__next = None

        if parent is not None:
            parent.next = self

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, p):
        self.__parent = p
        if p is not None:
            p.next = self

    @property
    def next(self):
        return self.__next

    @next.setter
    def next(self, n):
        self.__next = n

class ControlFlowBlock(Root):
    def __init__(self, parent = None):
        Root.__init__(self, parent)
        self.true_block = None
        self.false_block = None
        self.cmp_inst = None

    def __str__(self):
        s = "CFB: True: %s <--> False: %s" % (self.true_block, self.false_block)
        return s

class MergedBlock(Root):
    def __init__(self, bb, parent=None, next=None):
        Root.__init__(self, parent)
        self.bb = bb

    def __str__(self):
        s = "Merged: %s" % self.bb
        return s

class StructurizerAnalysisPass(FunctionPass, IRBaseVisitor):
    """
    This pass defines the Loopy Algorithm for structurizing basic blocks.
    Read about the algorithm at (http://ssarangi.github.io/2016/01/20/Loopy-Structurizer/)
    """
    def __init__(self):
        FunctionPass.__init__(self)
        IRBaseVisitor.__init__(self)
        self.control_flow_stack = []
        self.root_node = None

        self.cfb_blocks = {}
        self.merged_blocks = {}

    def create_nested_and_cfb_blocks(self, func):
        for bb in func.basic_blocks:
            merged_bb = MergedBlock(bb)
            self.merged_blocks[bb] = merged_bb
            terminator = bb.get_terminator()
            if isinstance(terminator, ConditionalBranchInstruction):
                cfb = ControlFlowBlock(self.merged_blocks[bb])
                self.cfb_blocks[bb] = cfb
                merged_bb.next = cfb

    def get_cfb(self, bb):
        return self.cfb_blocks[bb]

    def get_merged_bb(self, bb):
        return self.merged_blocks[bb]

    def find_nearest_cfb_parent_block(self, nested_bb):
        while not isinstance(nested_bb, ControlFlowBlock):
            child = nested_bb
            nested_bb.processed = True

            if isinstance(nested_bb.parent, ControlFlowBlock) and \
            nested_bb.parent.processed is True:
                nested_bb = nested_bb.parent.parent
            else:
                nested_bb = nested_bb.parent

        assert isinstance(nested_bb, ControlFlowBlock)
        return nested_bb

    def merge_the_blocks(self, merged_bb, terminate_at=None):
        root = merged_bb
        merged_bb = merged_bb.next

        # Keep on merging the blocks till we hit a Control Flow Block
        while not isinstance(merged_bb, ControlFlowBlock) and terminate_at != merged_bb:
            for inst in merged_bb.bb.instructions:
                if not isinstance(inst, BranchInstruction):
                    root.bb.instructions.append(inst)
                    inst.parent = root.bb

            merged_bb = merged_bb.next

        if terminate_at is not None:
            self.merge(root.next)
        else:
            root.next = merged_bb
            self.merge(merged_bb)

    def merge_the_cfb(self, cfb):
        self.merge_the_blocks(cfb.true_block, cfb.next)
        self.merge_the_blocks(cfb.false_block, cfb.next)

    def merge(self, merge_node):
        if isinstance(merge_node, MergedBlock):
            self.merge_the_blocks(merge_node)
        elif isinstance(merge_node, ControlFlowBlock):
            self.merge_the_cfb(merge_node)

    @verify(node=Function)
    def run_on_function(self, node):
        draw_header("Structurizer: %s" % node.name)
        func = node

        self.create_nested_and_cfb_blocks(func)

        # Create a new queue for BFS
        queue = Queue()

        self.root_node = self.get_merged_bb(func.entry_block)
        queue.put(self.root_node)

        visited = []
        while not queue.empty():
            merged_bb = queue.get()
            bb = merged_bb.bb

            process = True
            if bb in visited and not merged_bb.processed:
                # Then we have found a terminating condition.
                # Find the root off this control flow block
                converge_point = merged_bb

                cfb = self.find_nearest_cfb_parent_block(merged_bb)
                cfb.next = converge_point
                process = False
                cfb.processed = True

            visited.append(bb)

            if process:
                terminator = bb.get_terminator()
                if isinstance(terminator, ConditionalBranchInstruction):
                    # Start a visited stack
                    # Start with an If-else block
                    cfb = self.get_cfb(bb)
                    cfb.true_block = self.get_merged_bb(terminator.bb_true)
                    cfb.true_block.parent = cfb
                    cfb.false_block = self.get_merged_bb(terminator.bb_false)
                    cfb.false_block.parent = cfb

                    cfb.parent = merged_bb

                    self.control_flow_stack.append(cfb)

                    queue.put(cfb.true_block)
                    queue.put(cfb.false_block)

                elif isinstance(terminator, BranchInstruction):
                    # Find the branch where it terminates to
                    branch_to_bb = terminator.basic_block
                    branch_to_bb_merged = self.get_merged_bb(branch_to_bb)
                    branch_to_bb_merged.parent = merged_bb
                    queue.put(merged_bb.next)

                else:
                    assert isinstance(terminator, ReturnInstruction)


        node = self.root_node

        # Merge all the branches which have a branch instruction. Stop only when we see Conditional branch
        self.merge(node)
        print("-" * 100)