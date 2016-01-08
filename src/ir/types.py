__author__ = 'sarangis'

from ir.exceptions import *

class BaseType:
    def __init__(self):
        pass

    # def __new__(cls, *args, **kwargs):
    #     if cls is BaseType:
    #         raise TypeError("base class may not be instantiated")
    #     return object.__new__(cls, *args, **kwargs)

class IntType(BaseType):
    def __init__(self, bitSize):
        BaseType.__init__(self)
        self.__bitsize = bitSize

    @property
    def bits(self):
        return self.__bitsize

    def __str__(self):
        output_str = ""
        output_str += "i" + str(self.__bitsize)
        return output_str

class FloatType(BaseType):
    def __init__(self):
        BaseType.__init__(self)

    def __str__(self):
        return "float"

class DoubleType(BaseType):
    def __init__(self):
        BaseType.__init__(self)

    def __str__(self):
        return "d64"

class BoolType(IntType):
    def __init__(self):
        IntType.__init__(8)

    def __str__(self):
        return "bool"

class BitType(IntType):
    def __init__(self):
        IntType.__init__(1)

    def __str__(self):
        return str(IntType.__str__())

class ByteType(IntType):
    def __init__(self):
        IntType.__init__(8)

    def __str__(self):
        return str(IntType.__str__())

class VectorType(BaseType):
    def __init__(self, base_ty, numElts):
        self.__baseTy = base_ty
        self.__numElts = numElts

    @property
    def baseTy(self):
        return self.__baseTy

    @property
    def numElts(self):
        return self.__numElts

class PointerType(BaseType):
    def __init__(self, base_type, address_space):
        if not isinstance(base_type, BaseType):
            raise InvalidTypeException("Expected pointer to a base type (int, float, double, pointer)")

        if not isinstance(address_space, int):
            raise IllegalArgumentException("Expected address space to be an integer")

        self.__base_type = base_type
        self.__address_space = address_space

    def __str__(self):
        output_str = ""
        output_str += str(self.__base_type) + " addrspace(" + str(self.__address_space) + ")*"
        return output_str


class FunctionType(BaseType):
    def __init__(self, ret_type, *arg_types):
        BaseType.__init__(self)
        if not isinstance(ret_type, BaseType):
            raise InvalidTypeException("Return type should be derived from BaseType")

        self.__ret_type = ret_type

        for arg_type in arg_types:
            if not isinstance(arg_type, BaseType):
                raise InvalidTypeException("Arg type should be derived from BaseType")

        self.__arg_types = arg_types

    @property
    def ret_type(self):
        return self.__ret_type

    @property
    def arg_types(self):
        return self.__arg_types

    def __str__(self):
        final_output_str = str(self.__ret_type) + " ()* "

        output_str = "("
        for idx, i in enumerate(self.__arg_types):
            output_str += str(i)
            if idx < len(self.__arg_types) - 1:
                output_str += ", "

        output_str += ")"

        final_output_str += output_str
        return final_output_str