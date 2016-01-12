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

from src.optimizer.const_propagation import ConstPropagationPass
from src.optimizer.passmanager import PassManager
from src.codegen.x86codegen import x86CodeGen
from src.codegen.jscodegen import JSCodeGen

from src.utils.print_utils import draw_header
from src.py2ir.generate_ir import IRGenerator

import src.pyasm2.x86 as x86

import src.pyasm2.jitter as jitter

def create_bytes(byte_list):
    x86bytes = bytes(byte_list)
    return x86bytes

def create_ast(source, filename):
    tree = ast.parse(source, filename, 'exec')
    return tree

def generate_ir(tree):
    ir_generator = IRGenerator()
    ir_generator.visit(tree)

    module = ir_generator.module
    draw_header("IR")
    print(module)

    # codegen = x86CodeGen()
    codegen = JSCodeGen()
    passmgr = PassManager()
    # passmgr.add_function_pass(ConstPropagationPass())
    passmgr.add_module_pass(codegen)
    passmgr.run(module)

    # block = x86.Block()
    # block.append(x86.imul(x86.eax, x86.ebx))
    #
    # inst = x86.mov(x86.eax, 50)
    # b = inst.bytes()
    #
    # bytes = block.assemble()
    # inst = x86.imul(x86.eax, x86.ebx)
    # b = inst.bytes()

    # bytes = codegen.get_assembly_bytes()
    # print(bytes)
    # x86bytes = create_bytes(bytes)

    # x86bytes = x86.mov(x86.eax, 50).bytes()
    # x86bytes += x86.ret().bytes()
    #
    # x86bytes = bytes(x86bytes)

    # x86 Code Generation
    # res = jitter.jit(x86bytes)
    # print("Function Return Result: %s" % res)

    # Javascript Code Generation
    js = codegen.get_code()
    print(js)


def main():
    filename = sys.argv[1]
    fptr = open(filename, "r")
    source = fptr.read()

    draw_header("Python Source")
    print(source)
    tree = create_ast(source, filename)
    generate_ir(tree)

if __name__ == "__main__":
    main()