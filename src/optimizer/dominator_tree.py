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

from queue import Queue
from src.ir.instructions import *
from src.ir.validator import *

class DominanceTree:
    def __init__(self):
        self.__root = None
        self.__doms = {}

    @property
    def root(self):
        return self.__root

    @root.setter
    def root(self, node):
        # self.__root = self.find_node(node)
        # if self.__root is None:
        #     self.__root = DominanceTree.get_new_node(node)

        self.__root = node
        self.__root.parent = None

    def add_dom(self, blk, dom):
        self.__doms[blk] = dom

    def add_dom_blk(self, blk, dom_blk):
        if blk not in self.__doms:
            self.__doms[blk] = [dom_blk]
        else:
            self.__doms[blk].append(dom_blk)

    def get_dom(self, blk):
        return self.__doms[blk]

    @verify(dominator=U(BasicBlock, Instruction), dominated=U(BasicBlock, Instruction))
    def dominates(self, dominator, dominated):
        blk_dominator = dominator
        blk_dominated = dominated

        if isinstance(dominator, Instruction):
            blk_dominator = dominator.parent

        if isinstance(dominated, Instruction):
            blk_dominated = dominated.parent

        if blk_dominated not in self.__doms:
            raise Exception("Dominator tree information not present for Block: %s" % blk_dominated.name)

        dominators = self.__doms[blk_dominated]

        for dom in dominators:
            if dom == blk_dominator:
                return True

        return False

    def __str__(self):
        str = ""
        for blk, doms in self.__doms.items():
            str += "%s --> %s\n" % (blk, doms)

        return str

    def __repr__(self):
        return str(self.__root)