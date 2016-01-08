__author__ = 'sarangis'

from ir.types import *
from ir.validator import *

class Value:
    def __init__(self):
        pass

class Argument(Value):
    def __init__(self, name, arg_type=None):
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
        return self.__name

    __repr__ = __str__