__author__ = 'sarangis'

from ir.utils import *
from ir.constants import *

class InstructionList(list):
    def __init__(self, name_generator):
        list.__init__(self)
        self.__name_generator = name_generator

    def append(self, inst):
        if inst.needs_name:
            inst.name = self.__name_generator.generate(inst)

        list.append(self, inst)

    def insert(self, idx, inst):
        if inst.needs_name:
            inst.name = self.__name_generator.generate(inst)

        list.insert(self, idx, inst)


    def __add__(self, other):
        raise NotImplementedError("__add__ method not implemented for InstructionList")


class Instruction(Value):
    @verify(operands=list)
    def __init__(self, operands=[], parent=None, name=None, needs_name=True):
        Value.__init__(self)
        self.__parent = parent
        self.__inst_idx = -1
        self.__name = name
        self.__needs_name = needs_name

        self.__operands = operands
        self.__uses = []

        for operand in operands:
            if isinstance(operand, Instruction):
                operand.add_use(self)

    @property
    def uses(self):
        return self.__uses

    def add_use(self, use):
        self.__uses.append(use)

    @property
    def operands(self):
        return tuple(self.__operands)

    @property
    def needs_name(self):
        return self.__needs_name

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, bb):
        self.__parent = bb

    @property
    def inst_idx(self):
        return self.__inst_idx

    @inst_idx.setter
    def inst_idx(self, v):
        self.__inst_idx = v

    @property
    def name(self):
        if self.__name is None:
            return None

        return "%" + self.__name

    @name.setter
    def name(self, n):
        self.__name = n

    def __str__(self):
        pass

    __repr__ = __str__


class CallInstruction(Instruction):
    def __init__(self, func, arg_list, parent=None, name=None):
        Instruction.__init__(self, [func] + arg_list, parent, name)
        self.__func = func

        # Verify the Args
        self.__func.verify_args(arg_list)
        self.__args = arg_list
        self.__type = self.__func.type

    @property
    def type(self):
        return self.__type

    @property
    def function(self):
        return self.__func

    @property
    def args(self):
        return self.__args

    def __str__(self):
        functype = self.__func.type
        output_str = "call " + str(functype.ret_type) + " @" + self.__func.name

        output_str += render_list_with_parens(self.__args)

        return output_str

    __repr__ = __str__


class TerminateInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass


class ReturnInstruction(Instruction):
    def __init__(self, value=None, parent=None, name=None):
        Instruction.__init__(self, [value], parent, name, needs_name=False)
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __str__(self):
        if self.__value is None:
            output_str = "return void"
        elif hasattr(self.__value, "name"):
            output_str = "return " + str(self.__value.name)
        else:
            output_str = "return " + str(self.__value)
        return output_str

    __repr__ = __str__


class SelectInstruction(Instruction):
    def __init__(self, cond, val_true, val_false, parent=None, name=None):
        Instruction.__init__(self, [cond, val_true, val_false], parent, name)
        self.__cond = cond
        self.__val_true = val_true
        self.__val_false = val_false

    @property
    def condition(self):
        return self.__cond

    @property
    def val_true(self):
        return self.__val_true

    @property
    def val_false(self):
        return self.__val_false

    def __str__(self):
        output_str = "select " + str(self.__cond) + " " + str(self.__val_true) + " " + str(self.__val_false)
        return output_str

    __repr__ = __str__


class LoadInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass


class StoreInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name, needs_name=False)

    def __str__(self):
        pass


class BinOpInstruction(Instruction):
    OP_ADD = 0
    OP_SUB = 1
    OP_MUL = 2
    OP_DIV = 3

    def __init__(self, binop, lhs, rhs, parent=None, name=None):
        Instruction.__init__(self, [lhs, rhs], parent, name)
        self.__operator = binop
        self.__lhs = lhs
        self.__rhs = rhs
        self.__type = self.__lhs.type

    @property
    def type(self):
        return self.__type

    @property
    def operator(self):
        return self.__operator

    @property
    def lhs(self):
        return self.__lhs

    @property
    def rhs(self):
        return  self.__rhs

    def __str__(self):
        if self.__operator == BinOpInstruction.OP_ADD:
            output_str = "add"
        elif self.__operator == BinOpInstruction.OP_SUB:
            output_str = "sub"
        elif self.__operator == BinOpInstruction.OP_MUL:
            output_str = "mul"
        elif self.__operator == BinOpInstruction.OP_DIV:
            output_str = "div"
        else:
            raise InvalidTypeException("BinOp instruction expects, OP_ADD, OP_SUB, OP_MUL, OP_DIV")

        output_str += render_list_with_parens(self.operands)
        return output_str

    __repr__ = __str__


class AddInstruction(BinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        BinOpInstruction.__init__(self, BinOpInstruction.OP_ADD, lhs, rhs, parent, name)

class SubInstruction(BinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        BinOpInstruction.__init__(self, BinOpInstruction.OP_SUB, lhs, rhs, parent, name)

class MulInstruction(BinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        BinOpInstruction.__init__(self, BinOpInstruction.OP_MUL, lhs, rhs, parent, name)

class DivInstruction(BinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        BinOpInstruction.__init__(self, BinOpInstruction.OP_DIV, lhs, rhs, parent, name)


class FBinOpInstruction(Instruction):
    OP_ADD = 0
    OP_SUB = 1
    OP_MUL = 2
    OP_DIV = 3

    def __init__(self, binop, lhs, rhs, parent=None, name=None):
        Instruction.__init__(self, [lhs, rhs], parent, name)
        self.__operator = binop
        self.__lhs = lhs
        self.__rhs = rhs

    @property
    def operator(self):
        return self.__operator

    @property
    def lhs(self):
        return self.__lhs

    @property
    def rhs(self):
        return  self.__rhs

    def __str__(self):
        if self.__operator == BinOpInstruction.OP_ADD:
            output_str = "fadd"
        elif self.__operator == BinOpInstruction.OP_SUB:
            output_str = "fsub"
        elif self.__operator == BinOpInstruction.OP_MUL:
            output_str = "fmul"
        elif self.__operator == BinOpInstruction.OP_DIV:
            output_str = "fdiv"
        else:
            raise InvalidTypeException("FBinOp instruction expects, OP_ADD, OP_SUB, OP_MUL, OP_DIV")

        output_str += render_list_with_parens(self.operands)
        return output_str

    __repr__ = __str__

class FAddInstruction(FBinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        FBinOpInstruction.__init__(self, FBinOpInstruction.OP_ADD, lhs, rhs, parent, name)

class FSubInstruction(FBinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        FBinOpInstruction.__init__(self, FBinOpInstruction.OP_SUB, lhs, rhs, parent, name)

class FMulInstruction(FBinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        FBinOpInstruction.__init__(self, FBinOpInstruction.OP_MUL, lhs, rhs, parent, name)

class FDivInstruction(FBinOpInstruction):
    def __init__(self, lhs, rhs, parent=None, name=None):
        FBinOpInstruction.__init__(self, FBinOpInstruction.OP_DIV, lhs, rhs, parent, name)

class AllocaInstruction(Instruction):
    def __init__(self, alloca_type, numEls=None, align=None, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)
        self.__alloca_type = alloca_type
        self.__numEls = numEls
        self.__align = align

    @property
    def type(self):
        return PointerType(self.__alloca_type, 0)

    @property
    def numEls(self):
        return self.__numEls

    @property
    def alignment(self):
        return self.__align

    def __str__(self):
        output_str = "alloca "
        output_str += str(self.type) + " "
        if self.numEls is not None:
            output_str += ", i32 %s" % self.numEls

        if self.alignment is not None:
            output_str += ", align %s" % self.alignment

        return output_str

    __repr__ = __str__


class PhiInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass


class BranchInstruction(Instruction):
    def __init__(self, bb, parent=None, name=None):
        Instruction.__init__(self, [bb], parent, name, needs_name=False)
        self.__bb = bb

        if parent is not None:
            parent.add_successor = bb
            bb.add_predecesssor = parent

    def __str__(self):
        output_str = "br " + self.__bb.name
        return output_str


class ConditionalBranchInstruction(Instruction):
    def __init__(self, cmp_inst, value, bb_true, bb_false, parent=None, name=None):
        Instruction.__init__(self, [cmp_inst, bb_true, bb_false], parent, name)
        self.__cmp_inst = cmp_inst
        self.__value = value
        self.__bb_true = bb_true
        self.__bb_false = bb_false

        if parent is not None:
            parent.add_successor(bb_true)
            parent.add_successor(bb_false)
            bb_true.add_predecessor(parent)
            bb_false.add_predecessor(parent)

    @property
    def cmp_inst(self):
        return self.__cmp_inst

    @property
    def cmp_value(self):
        return self.__value

    @property
    def bb_true(self):
        return self.__bb_true

    @property
    def bb_false(self):
        return self.__bb_false

    def __str__(self):
        output_str = "br "
        output_str += self.__cmp_inst.name + " "
        output_str += str(self.__value) + ","
        output_str += " label %" + str(self.__bb_true.name) + ", label %" + str(self.__bb_false.name)
        return output_str


class IndirectBranchInstruction(BranchInstruction):
    def __init__(self, bb, parent=None, name=None):
        BranchInstruction.__init__(self, bb, parent, name)

    def __str__(self):
        pass


class SwitchInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass

class CompareTypes:
    EQ = 1
    NE = 2
    UGT = 3
    UGE = 4
    ULT = 5
    ULE = 6
    SGT = 7
    SGE = 8
    SLT = 9
    SLE = 10

    @staticmethod
    def get_str(compareTy):
        if compareTy == CompareTypes.EQ: return "eq"
        elif compareTy == CompareTypes.NE: return "ne"
        elif compareTy == CompareTypes.UGT: return "ugt"
        elif compareTy == CompareTypes.UGE: return "uge"
        elif compareTy == CompareTypes.ULT: return "ult"
        elif compareTy == CompareTypes.ULE: return "ule"
        elif compareTy == CompareTypes.SGT: return "sgt"
        elif compareTy == CompareTypes.SGE: return "sge"
        elif compareTy == CompareTypes.SLT: return "slt"
        elif compareTy == CompareTypes.SLE: return "sle"

class CompareInstruction(Instruction):
    def __init__(self, cond, op1, op2, parent=None, name=None):
        Instruction.__init__(self, [op1, op2], parent, name)
        self.__condition = cond
        self.__op1 = op1
        self.__op2 = op2

    @property
    def condition(self):
        return self.__condition

    @property
    def op1(self):
        return self.__op1

    @property
    def op2(self):
        return self.__op2

    def __str__(self):
        return "Compare Instruction"

    __repr__ = __str__

class ICmpInstruction(CompareInstruction):
    def __init__(self, cond, op1, op2, parent=None, name=None):
        CompareInstruction.__init__(self, cond, op1, op2, parent, name)

    def __str__(self):
        output_str = "icmp "
        output_str += CompareTypes.get_str(self.condition)
        output_str += " " + str(self.op1) + ", " + str(self.op2)
        return output_str

    __repr__ = __str__

class FCmpInstruction(CompareInstruction):
    def __init__(self, cond, op1, op2, parent=None, name=None):
        CompareInstruction.__init__(self, cond, op1, op2, parent, name)

    def __str__(self):
        output_str = "fcmp "
        output_str += CompareTypes.get_str(self.condition)
        output_str += " " + str(self.op1) + ", " + str(self.op2)
        return output_str


    __repr__ = __str__

class CastInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass

    __repr__ = __str__

class GEPInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass

    __repr__ = __str__

class ExtractElementInstruction(Instruction):
    def __init__(self, vec, idx, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)
        self.__vec = vec
        self.__idx = idx

    @property
    def vec(self):
        return self.__vec

    @property
    def idx(self):
        return self.__idx

    def __str__(self):
        pass

    __repr__ = __str__

class InsertElementInstruction(Instruction):
    def __init__(self, parent=None, name=None):
        Instruction.__init__(self, [], parent, name)

    def __str__(self):
        pass

    __repr__ = __str__

class BitwiseBinaryInstruction(Instruction):
    SHL = 0
    LSHR = 1
    ASHR = 2
    AND = 3
    OR = 4
    XOR = 5

    def __init__(self, op, op1, op2, parent=None, name=None):
        Instruction.__init__(self, [op1, op2], parent, name)
        self.__op1 = op1
        self.__op2 = op2
        self.__operator = op

    @property
    def op1(self):
        return self.__op1

    @property
    def op2(self):
        return self.__op2

    def __str__(self):
        if self.__operator == BitwiseBinaryInstruction.SHL:
            output_str = "shl"
        elif self.__operator == BitwiseBinaryInstruction.LSHR:
            output_str = "lshr"
        elif self.__operator == BitwiseBinaryInstruction.ASHR:
            output_str = "ashr"
        elif self.__operator == BitwiseBinaryInstruction.AND:
            output_str = "and"
        elif self.__operator == BitwiseBinaryInstruction.OR:
            output_str = "or"
        elif self.__operator == BitwiseBinaryInstruction.XOR:
            output_str = "xor"
        else:
            raise InvalidTypeException("Invalid Bitwise Binary operator: %s encountered" % self.__operator)

        output_str += " " + str(self.__op1) + ", " + str(self.__op2)
        return output_str

    __repr__ = __str__

class ShiftLeftInstruction(BitwiseBinaryInstruction):
    def __init__(self, op1, op2, parent=None, name=None):
        BitwiseBinaryInstruction.__init__(self, BitwiseBinaryInstruction.SHL, op1, op2, parent, name)


class LogicalShiftRightInstruction(BitwiseBinaryInstruction):
    def __init__(self, op1, op2, parent=None, name=None):
        BitwiseBinaryInstruction.__init__(self, BitwiseBinaryInstruction.LSHR, op1, op2, parent, name)


class ArithmeticShiftRightInstruction(BitwiseBinaryInstruction):
    def __init__(self, op1, op2, parent=None, name=None):
        BitwiseBinaryInstruction.__init__(self, BitwiseBinaryInstruction.ASHR, op1, op2, parent, name)


class AndInstruction(BitwiseBinaryInstruction):
    def __init__(self, op1, op2, parent=None, name=None):
        BitwiseBinaryInstruction.__init__(self, BitwiseBinaryInstruction.AND, op1, op2, parent, name)


class OrInstruction(BitwiseBinaryInstruction):
    def __init__(self, op1, op2, parent=None, name=None):
        BitwiseBinaryInstruction.__init__(self, BitwiseBinaryInstruction.OR, op1, op2, parent, name)


class XorInstruction(BitwiseBinaryInstruction):
    def __init__(self, op1, op2, parent=None, name=None):
        BitwiseBinaryInstruction.__init__(self, BitwiseBinaryInstruction.XOR, op1, op2, parent, name)


class BasicBlock(Validator):
    def __init__(self, name, parent):
        self.__name = name
        self.__parent = parent
        self.__instructions = InstructionList(parent.name_generator)
        self.__predecessors = []
        self.__successors = []

    @property
    def predecessors(self):
        return self.__predecessors

    @property
    def successors(self):
        return self.__successors

    def add_predecessor(self, predecessor):
        self.__predecessors.append(predecessor)

    def add_successor(self, successor):
        self.__successors.append(successor)

    @property
    def name(self):
        return self.__name

    @property
    def instructions(self):
        return self.__instructions

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, bb):
        self.__parent = bb

    @verify(inst=Instruction)
    def find_instruction_idx(self, inst):
        for idx, i in enumerate(self.__instructions):
            if i == inst:
                return idx

        return None

    def validate(self):
        error_str = self.__name + " BB has not terminator instruction"
        # Get the last instruction and make sure its the terminator
        if len(self.__instructions) > 0:
            last_inst = self.__instructions[len(self.__instructions) - 1]
            if not is_terminator_instruction(last_inst):
                raise NoBBTerminatorException(error_str)
        else:
            raise NoBBTerminatorException(error_str)

    def render(self):
        predecessor_names = [p.name for p in self.__predecessors]
        output_str = self.name + ": "
        if len(predecessor_names) > 0:
            output_str += "; pred: " + str(predecessor_names)

        output_str += "\n"
        for i in self.__instructions:
            output_str += " " * 4

            if i.name is not None:
                output_str += i.name + " = "

            output_str += str(i) + "\n"

        return output_str

    def __str__(self):
        return self.name

    __repr__ = __str__