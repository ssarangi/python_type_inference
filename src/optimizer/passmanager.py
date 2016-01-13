__author__ = 'sarangis'

from src.ir.module import *
from src.ir.function import *
from src.optimizer.pass_support import *

class PassManager:
    def __init__(self):
        self.__passes = []

    @verify(function_pass=FunctionPass)
    def add_function_pass(self, function_pass):
        self.__passes.append(function_pass)

    @verify(module_pass=ModulePass)
    def add_module_pass(self, module_pass):
        self.__passes.append(module_pass)

    @verify(module=U(Function, Module))
    def run(self, module):
        for p in self.__passes:
            if isinstance(p, ModulePass):
                p.run_on_module(module)
            elif isinstance(p, FunctionPass):
                for name, f in module.functions.items():
                    p.run_on_function(f)
            elif isinstance(p, InstVisitorPass):
                p.visit(module)
            else:
                raise InvalidTypeException("Invalid pass types")