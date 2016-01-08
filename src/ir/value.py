__author__ = 'sarangis'

from ir.types import *
from ir.validator import *

class Value:
    def __init__(self):
        pass

class Argument(Value):
    def __init__(self, arg_type, name):
        Value.__init__(self)
        self.__name = name
        self.__type = arg_type

    @property
    def name(self):
        return self.__name

    @property
    def type(self):
        return self.__type

    def __str__(self):
        output_str = str(self.__type) + " " + "%" + str(self.__name)
        return output_str

    __repr__ = __str__