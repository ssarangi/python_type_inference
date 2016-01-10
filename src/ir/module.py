__author__ = 'sarangis'

from src.ir.exceptions import *
from src.ir.validator import *
from src.ir.context import *

class Module(Validator):
    @verify(name=str, ctx=Context)
    def __init__(self, name, ctx):
        self.__context = ctx
        self.__name = name
        self.__globals = []
        self.__functions = {}
        self.__func_declarations = []
        self.__data_layout = []
        self.__target_arch = ""
        self.__entry_point = None
        self.__db_strings = []

    @property
    def globals(self):
        return self.__globals

    def add_global(self, globalv):
        self.__globals.append(globalv)

    @property
    def functions(self):
        return self.__functions

    @property
    def function_decls(self):
        return self.__func_declarations

    @function_decls.setter
    def function_decls(self, func_decl):
        self.__func_declarations.append(func_decl)

    @property
    def datalayout(self):
        return self.__data_layout

    @datalayout.setter
    def datalayout(self, dl):
        self.__data_layout = dl

    @property
    def target_arch(self):
        return self.__target_arch

    @target_arch.setter
    def target_arch(self, arch):
        self.__target_arch = arch

    @property
    def name(self):
        return self.__name

    @property
    def context(self):
        return self.__context

    @property
    def entry_point(self):
        return self.__entry_point

    @entry_point.setter
    def entry_point(self, function):
        assert function.name in self.__functions.keys(), "Function not present in module"
        self.__entry_point = function

    def add_to_db_string(self, string):
        self.__db_strings.append(string)

    def __str__(self):
        output_str = ""
        output_str += "Module: %s\n" % (self.__name)

        for f in self.__func_declarations:
            output_str += str(f)

        for name, f in self.__functions.items():
            output_str += str(f)

        return output_str

    def validate(self):
        for f in self.__functions:
            f.validate()

    __repr__ = __str__