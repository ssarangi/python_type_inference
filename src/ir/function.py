__author__ = 'sarangis'

from src.ir.exceptions import *
from src.ir.validator import *
from src.ir.instructions import Instruction, BasicBlock

class Global:
    def __init__(self, name, initializer):
        self.__name = name
        self.__initializer = initializer

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

        self.__bb_idx = 0
        self.__bb_names = {}

    def __get_variable_idx(self):
        current_idx = self.__variable_idx
        self.__variable_idx += 1
        return str(current_idx)

    def __get_basic_block_idx(self):
        current_idx = self.__bb_idx
        self.__bb_idx += 1
        return str(current_idx)

    def __get_named_var_idx(self, name):
        new_name = name
        if name in self.__named_variables:
            new_name += str(self.__named_variables[name] + 1)
            self.__named_variables[name] += 1
        else:
            self.__named_variables[name] = 0

        return new_name

    def __get_named_bb_idx(self, name):
        new_name = name
        if name in self.__bb_names:
            new_name += "_" + str(self.__bb_names[name] + 1)
            self.__bb_names[name] += 1
        else:
            self.__bb_names[name] = 0

        return new_name

    @verify(inst=Instruction)
    def generate(self, inst):
        if inst.name is None:
            return self.__get_variable_idx()
        else:
            return self.__get_named_var_idx(inst.name)

    @verify(bb_name=str)
    def generate_bb(self, bb_name):
        if bb_name is None:
            return "bb_%s" % self.__get_basic_block_idx()
        else:
            return self.__get_named_bb_idx(bb_name)


class Function(Validator):
    def __init__(self, name, args=None):
        self.__basic_blocks = []
        self.__name = name

        self.__arguments = args
        self.__name_generator = NameGenerator()
        self.__entry_block = None
        self.__exit_block = None

    @property
    def entry_block(self):
        if self.__entry_block is not None:
            return self.__entry_block

        for bb in self.__basic_blocks:
            if bb.name == "entry":
                self.__entry_block = bb
                return bb

        raise Exception("No Entry basic block found in function: %s" % self.__name)

    @property
    def exit_block(self):
        if self.__exit_block is not None:
            return self.__exit_block

        for bb in self.__basic_blocks:
            if bb.name == "exit":
                self.__exit_block = bb
                return bb

        return None

    @property
    def name_generator(self):
        return self.__name_generator

    @property
    def basic_blocks(self):
        return self.__basic_blocks

    @property
    def args(self):
        return self.__arguments

    @args.setter
    def args(self, arg_list):
        if not isinstance(arg_list, list):
            raise InvalidTypeException("Expected arg_list to be a list")

        self.__arguments = arg_list

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, n):
        self.__name = n

    def render_signature(self):
        output_str = ""
        output_str += "define " + " " + self.__name + "("

        for count, arg in enumerate(self.__arguments):
            output_str += str(arg)
            if count != len(self.__arguments) - 1:
                output_str += ", "

        output_str += ")"

        return output_str

    def __str__(self):
        output_str = ""
        output_str += "define " + " " + self.__name + "("

        for count, arg in enumerate(self.__arguments):
            output_str += arg.name
            if count != len(self.__arguments) - 1:
                output_str += ", "

        output_str += ") {\n"

        # render each basic block
        for bb in self.__basic_blocks:
            output_str += bb.render()

        output_str += "}"
        return output_str

    def validate(self):
        for bb in self.__basic_blocks:
            bb.validate()

    def __repr__(self):
        return self.__name