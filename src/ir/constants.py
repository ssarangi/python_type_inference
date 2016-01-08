__author__ = 'sarangis'

from ir.value import *

class Constant(Value):
    def __init__(self):
        Value.__init__(self)

    def __str__(self):
        pass

    __repr__ = __str__

class IntConstant(Constant):
    def __init__(self, bits, initializer):
        Constant.__init__(self)
        self.__type = IntType(bits)
        self.__initializer = initializer

    @property
    def initializer(self):
        return self.__initializer

    @property
    def name(self):
        return str(self.__initializer)

    @property
    def type(self):
        return self.__type

    def __str__(self):
        return str(self.__type) + " " + str(self.__initializer)

class BoolConstant(IntConstant):
    def __init__(self, initializer):
        IntConstant.__init__(self, 8, initializer)

    def __str__(self):
        return str(self.type) + " " + str(self.initializer)


class FloatConstant(Constant):
    def __init__(self, initializer):
        Constant.__init__(self)
        self.__initializer = initializer

    @property
    def initializer(self):
        return self.__initializer

    @property
    def name(self):
        return str(self.__initializer)

    @property
    def type(self):
        return self.__type

    def __str__(self):
        return str(self.__type) + " " + str(self.__initializer)


class DoubleConstant(Constant):
    def __init__(self, initializer):
        Constant.__init__(self)
        self.__initializer = initializer

    @property
    def initializer(self):
        return self.__initializer

    @property
    def name(self):
        return str(self.__initializer)

    @property
    def type(self):
        return self.__type

    def __str__(self):
        return str(self.__type) + " " + str(self.__initializer)

class StrConstant(Constant):
    def __init__(self):
        Constant.__init__(self)

    @property
    def initializer(self):
        return self.__initializer

    @property
    def name(self):
        return str(self.__initializer)

    @property
    def type(self):
        return self.__type

    def __str__(self):
        return ""


class Vector(Value):
    def __init__(self, vecTy):
        self.__vecTy = vecTy

    def type(self):
        return self.__vecTy
