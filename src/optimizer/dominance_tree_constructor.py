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

from src.optimizer.pass_support import *
from src.optimizer.dominator_tree import DominanceTree
from src.optimizer.cfg_traversal import post_order_traversal, reverse_post_order_traversal

class DominatorTreeConstructorPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)
        self.dom_tree = None

    def run_on_function(self, func):
        draw_header("Dominator Tree Constructor")

        dom_tree = DominanceTree()

        start_node = func.entry_block
        dom_tree.add_dom_blk(start_node, start_node)

        for bb in func.basic_blocks:
            if bb != start_node:
                dom_tree.add_dom(bb, [bb for bb in func.basic_blocks])

        changed = True
        while changed:
            changed = False

            reverse_post_order_blks = reverse_post_order_traversal(func)

            for blk in reverse_post_order_blks:
                # For each n in N - {n0}
                if blk != start_node:
                    new_idom = set(dom_tree.get_dom(blk))
                    for pred in blk.predecessors:
                        doms = dom_tree.get_dom(pred)

                        doms = set(doms)
                        new_idom = new_idom.intersection(doms)
                        new_idom.add(blk)

                    prev_dom = dom_tree.get_dom(blk)
                    new_idom = list(new_idom)
                    if new_idom != prev_dom:
                        dom_tree.add_dom(blk, new_idom)
                        changed = True

        self.dom_tree = dom_tree
        print(dom_tree)

class PostDominatorTreeConstructorPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)
        self.post_dom_tree = None

    def run_on_function(self, func):
        draw_header("Post Dominator Tree Constructor")

        post_dom_tree = DominanceTree()

        start_node = func.exit_block
        post_dom_tree.add_dom_blk(start_node, start_node)

        for bb in func.basic_blocks:
            if bb != start_node:
                post_dom_tree.add_dom(bb, [bb for bb in func.basic_blocks])

        changed = True
        while changed:
            changed = False

            post_order_blks = post_order_traversal(func)

            for blk in post_order_blks:
                # For each n in N - {n0}
                if blk != start_node:
                    new_idom = set(post_dom_tree.get_dom(blk))
                    for pred in blk.successors:
                        doms = post_dom_tree.get_dom(pred)

                        doms = set(doms)
                        new_idom = new_idom.intersection(doms)
                        new_idom.add(blk)

                    prev_dom = post_dom_tree.get_dom(blk)
                    new_idom = list(new_idom)
                    if new_idom != prev_dom:
                        post_dom_tree.add_dom(blk, new_idom)
                        changed = True

        self.post_dom_tree = post_dom_tree
        print(post_dom_tree)