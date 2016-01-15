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

from src.utils.print_utils import draw_header

from src.ir.function import Function
from src.ir.validator import verify

from src.optimizer.pass_support import *
from src.optimizer.cfg_traversal import reverse_post_order_traversal

class DominanceTreeConstructorPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)
        self.doms = {}
        self.uniq = {}

    def get_doms(self):
        pass

    @verify(node=Function)
    def run_on_function(self, node):
        draw_header("Dominator Tree Constructor")

        dom_tree = {}
        bb_list = node.basic_blocks
        for bb in bb_list:
            dom_tree[bb] = None

        start_node = node.entry_block