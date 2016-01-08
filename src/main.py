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

import sys
import ast

from src.def_use_chain import DefUseChain
from src.const_folding_visitor import ConstFoldVisitor
from src.const_prop_visitor import ConstPropVisitor

def create_ast(source, filename):
    tree = ast.parse(source, filename, 'exec')
    return tree

def create_transformations(tree):
    const_fold = ConstFoldVisitor()
    const_fold.visit(tree)

    def_use_chain = DefUseChain()
    def_use_chain.visit(tree)

    const_fold = ConstFoldVisitor()
    # const_fold.visit(tree)

    # print(ast.dump(tree))

    const_prop = ConstPropVisitor()
    # const_prop.visit(tree)

def main():
    filename = sys.argv[1]
    fptr = open(filename, "r")
    source = fptr.read()
    tree = create_ast(source, filename)
    create_transformations(tree)

if __name__ == "__main__":
    main()