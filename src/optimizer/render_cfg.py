"""
The MIT License (MIT)

Copyright (c) 2015 <Satyajit Sarangi>

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

from src.optimizer.pass_support import *

from src.utils.print_utils import draw_header

from queue import Queue

class RenderCFGPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)

    def run_on_function(self, node):
        entry_block = node.basic_blocks[0]
        Q = Queue()
        Q.put(entry_block)

        indent = " " * 4
        dot_str = "digraph g {\n"
        dot_str += indent + "node [shape=box];\n"

        while not Q.empty():
            bb = Q.get()
            # Now from bb add all the successor blocks
            for succ in bb.successors:
                dot_str += indent + bb.name + " -> " + succ.name + ";\n"
                Q.put(succ)

        dot_str += "}"

        draw_header("Control Flow Graph: %s" % node.name)
        print("Visualize this graph at: http://mdaines.github.io/viz.js/")
        print(dot_str)
