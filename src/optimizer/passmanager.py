__author__ = 'sarangis'

from ir.module import *
from optimizer.pass_support import *

class PassManager:
    def __init__(self):
        self.__passes = []

    @verify(function_pass=FunctionPass)
    def add_function_pass(self, function_pass):
        self.__passes.append(function_pass)

    @verify(module_pass=ModulePass)
    def add_module_pass(self, module_pass):
        self.__passes.append(module_pass)

    @verify(module=Module)
    def run(self, module):
        for p in self.__passes:
            if isinstance(p, ModulePass):
                p.run_on_module(module)
            elif isinstance(p, FunctionPass):
                for f in module.functions:
                    p.run_on_function(f)
            elif isinstance(p, InstVisitorPass):
                p.visit(module)
            else:
                raise InvalidTypeException("Invalid pass types")