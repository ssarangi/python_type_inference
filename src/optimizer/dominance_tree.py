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

class DominanceNode:
    def __init__(self, node):
        self.actual_node = node
        self.children = set()
        self.parent = None

    def get_dominators(self):
        pass


class DominanceTree:
    def __init__(self):
        self.root = None

    def set_root(self, node):
        self.root = self.find_node(node)
        if self.root is None:
            self.root = self.get_new_node(node)

        self.root.parent = None

    @staticmethod
    def get_new_node(self, node):
        return DominanceNode(node)

    def depth(self, key):
        node = self.find_node(key)
        depth = 0
        while node is not None:
            node = node.parent
            depth += 1

        return depth

    def set_idom(self, node, idom):
        dom_node = self.find_node(node)
        dom_idom = self.find_node(idom)

        if dom_node is None:
            dom_node = self.get_new_node(node)
        else:
            dom_node.parent.remove(dom_node)

        dom_idom.children.add(dom_node)

    def find_node(self, key):
        if self.root is None:
            return None

        visitQ = Queue()
        visitQ.put(self.root)

        while visitQ.not_empty:
            node = visitQ.get()
            if (node.actual_node == key):
                return node

            children = node.children
            for child in children:
                visitQ.put(child)

    def __str__(self):
        pass