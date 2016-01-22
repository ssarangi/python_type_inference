__author__ = 'sarangis'

from src.ir.value import *

class Constant(Value):
    def __init__(self):
        Value.__init__(self)

    def __str__(self):
        pass

    __repr__ = __str__

class ConstantNone(Value):
    def __init__(self):
        Value.__init__(self)

    def __str__(self):
        return "None"

    __repr__ = __str__

class Number(Constant):
    def __init__(self, number):
        Constant.__init__(self)
        self.number = number
        self.uses = []

    def __str__(self):
        return str(self.number)

    __repr__ = __str__

class String(Constant):
    def __init__(self, str):
        Constant.__init__(self)
        self.str = str
        self.uses = []

    def __str__(self):
        return self.str
