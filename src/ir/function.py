__author__ = 'sarangis'

from ir.exceptions import *
from ir.types import *
import ir.instructions
from ir.validator import *
from ir.value import *

class Global:
    def __init__(self, name, initializer):
        self.__name = name
        self.__initializer = initializer

    @property
    def type(self):
        return self.__initializer.type

    @property
    def name(self):
        return self.__name

    @property
    def initializer(self):
        return self.__initializer

    def __str__(self):
        return "%" + self.__name + " = " + str(self.__initializer)
 
    __repr__ = __str__

class NameGenerator:
    def __init__(self):
        self.__variable_idx = 0
        self.__named_variables = {}

    def __get_variable_idx(self):
        current_idx = self.__variable_idx
        self.__variable_idx += 1
        return str(current_idx)

    def __get_named_var_idx(self, name):
        new_name = name
        if name in self.__named_variables:
            new_name += str(self.__named_variables[name] + 1)
            self.__named_variables[name] += 1
        else:
            self.__named_variables[name] = 0

        return new_name

    @verify(inst=ir.instructions.Instruction)
    def generate(self, inst):
        if inst.name is None:
            return self.__get_variable_idx()
        else:
            return self.__get_named_var_idx(inst.name)


class Function(Validator):
    @verify(name=str, ftype=FunctionType)
    def __init__(self, name, ftype):
        self.__basic_blocks = []

        if not isinstance(name, str):
            raise InvalidTypeException("name is expected to be a string")

        self.__name = name

        if not isinstance(ftype, FunctionType):
            raise InvalidTypeException("Function Type expected")

        self.__type = ftype
        self.__arguments = [None] * len(ftype.arg_types)
        self.__name_generator = NameGenerator()

    @property
    def type(self):
        return self.__type

    @property
    def name_generator(self):
        return self.__name_generator

    @property
    def basic_blocks(self):
        return self.__basic_blocks

    @basic_blocks.setter
    def basic_blocks(self, block):
        return self.__basic_blocks.append(block)

    @property
    def args(self):
        return self.__arguments

    @args.setter
    def args(self, arg_list):
        if not isinstance(arg_list, list):
            raise InvalidTypeException("Expected arg_list to be a list")

        self.verify_args(arg_list)
        self.__arguments = arg_list

    # @verify(arg=Argument)
    # def insert_arg(self, arg, idx = None):
    #     if idx > len(self.__ftype.arg_types):
    #         raise InvalidUsageModel("Invalid argument type. Function supports %s arguments but argument to be "
    #                                 "added at index %s" % (len(self.__ftype.arg_types), idx))
    #
    #     # Check the function type for the number of args
    #     arg_type_idx = -1
    #     if idx is None:
    #         # Check the length of the arguments.
    #         arg_type_idx = len(self.__arguments)
    #     else:
    #         arg_type_idx = idx
    #
    #     print(arg_type_idx)
    #     # Now check if the index we got has the same type as the one in function type
    #     arg_type = self.__ftype.arg_types[arg_type_idx]
    #     # Make sure that the arg has the same type as the arg type
    #     print(type(arg_type))
    #     print(type(arg.type))
    #     if not isinstance(arg.type, arg_type):
    #         raise InvalidTypeException("Argument: " + str(arg) + " Expected: " + str(arg_type) + " Received: " + str(arg.type))
    #
    #     # Validate the arg
    #     if not isinstance(arg, Argument):
    #         raise InvalidTypeException("Argument type expected")
    #
    #     if idx is not None:
    #         # Check if the argument list is already that size
    #         if len(self.__arguments) > idx:
    #             self.__arguments.insert(idx, arg)
    #         else:
    #             current_len = len(self.__arguments)
    #             self.__arguments.append(arg)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, n):
        self.__name = n

    def render_signature(self):
        output_str = ""
        output_str += "define " + str(self.__ftype.ret_type) + " " + self.__name + "("

        for count, arg in enumerate(self.__arguments):
            output_str += str(arg)
            if count != len(self.__arguments) - 1:
                output_str += ", "

        output_str += ")"

        return output_str

    def __str__(self):
        output_str = ""
        output_str += "define " + str(self.__type.ret_type) + " " + self.__name + "("

        for count, arg in enumerate(self.__arguments):
            output_str += str(arg)
            if count != len(self.__arguments) - 1:
                output_str += ", "

        output_str += ") {\n"

        # render each basic block
        for bb in self.__basic_blocks:
            output_str += bb.render()

        output_str += "}\n\n"
        return output_str

    @verify(arg_list=list)
    def verify_args(self, arg_list):
       for idx, arg in enumerate(arg_list):
            if not type(arg.type) ==  type(self.__type.arg_types[idx]):
                raise InvalidTypeException("Expected %s to be of type: %s but received type: %s" %
                                           (arg.type, self.__type.arg_types[idx], type(arg.type)))

    def validate(self):
        for bb in self.__basic_blocks:
            bb.validate()

    __repr__ = __str__