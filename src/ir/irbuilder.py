__author__ = 'sarangis'

from src.ir.function import *
from src.ir.module import *
from src.ir.instructions import *

BINARY_OPERATORS = {
    '+':   lambda x, y: x + y,
    '-':   lambda x, y: x - y,
    '*':   lambda x, y: x * y,
    '**':  lambda x, y: x ** y,
    '/':   lambda x, y: x / y,
    '//':  lambda x, y: x // y,
    '<<':  lambda x, y: x << y,
    '>>':  lambda x, y: x >> y,
    '%':   lambda x, y: x % type(x)(y),
    '&':   lambda x, y: x & y,
    '|':   lambda x, y: x | y,
    '^':   lambda x, y: x ^ y,
}

class IRBuilder:
    """ The main builder to be used for creating instructions. This has to be used to insert / create / modify instructions
        This class will have to support all the other class creating it.
    """
    def __init__(self, current_module = None, context=None):
        self.__module = current_module
        self.__insertion_point = None
        self.__insertion_point_idx = 0
        self.__orphaned_instructions = []
        self.__context = context
        self.__current_bb = None

    @property
    def module(self):
        return self.__module

    @module.setter
    def module(self, mod):
        self.__module = mod

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, ctx):
        self.__context = ctx

    def get_current_bb(self):
        assert self.__current_bb is not None
        return self.__current_bb

    def insert_after(self, ip):
        if isinstance(ip, BasicBlock):
            self.__insertion_point = ip
            self.__insertion_point_idx = 0
            self.__current_bb = ip
        elif isinstance(ip, Instruction):
            self.__insertion_point = ip
            self.__insertion_point_idx = ip.parent.find_instruction_idx(ip)
            if self.__insertion_point_idx is None:
                raise InvalidInstructionException("Count not find instruction in its parent basic block")
            else:
                self.__insertion_point_idx += 1
        else:
            raise InvalidTypeException("Expected either Basic Block or Instruction")

    def insert_before(self, ip):
        if isinstance(ip, BasicBlock):
            self.__insertion_point = ip
            self.__insertion_point_idx = -1
            self.__current_bb = ip
        elif isinstance(ip, Instruction):
            self.__insertion_point = ip
            self.__insertion_point_idx = ip.parent.find_instruction_idx(ip)
            if self.__insertion_point_idx == None:
                raise InvalidInstructionException("Count not find instruction in its parent basic block")
            elif self.__insertion_point_idx == 0:
                self.__insertion_point_idx = 0
            else:
                self.__insertion_point_idx -= 1
        else:
            raise InvalidTypeException("Expected either Basic Block or Instruction")

    def __add_instruction(self, inst):
        if self.__insertion_point_idx == -1:
            # This is an orphaned instruction
            self.__orphaned_instructions.append(inst)
        elif isinstance(self.__insertion_point, BasicBlock):
            self.__insertion_point.instructions.append(inst)
            self.__insertion_point = inst
        elif isinstance(self.__insertion_point, Instruction):
            bb = self.__insertion_point.parent
            bb.instructions.insert(self.__insertion_point_idx + 1, inst)

            self.__insertion_point_idx += 1
            self.__insertion_point = inst
        else:
            raise Exception("Could not add instruction")

    def const_fold_binary_op(self, lhs, rhs, op):
        return None
        # if isinstance(lhs, Number) and isinstance(rhs, Number):
        #     lhs = lhs.number
        #     rhs = rhs.number
        #     result = BINARY_OPERATORS[op](lhs, rhs)
        #     return Number(result)
        # else:
        #     return None

    def create_function(self, name, args):
        f = Function(name, args)
        self.__module.functions[name] = f
        return f

    def set_entry_point(self, function):
        self.__module.entry_point = function

    def create_global(self, name, initializer):
        g = Global(name, initializer)
        self.__module.add_global(g)

    def create_basic_block(self, name, parent):
        bb = BasicBlock(name, parent)
        return bb

    def create_return(self, value = None, name=None):
        ret_inst = ReturnInstruction(value)
        self.__add_instruction(ret_inst)

    def create_branch(self, bb, name=None):
        if not isinstance(bb, BasicBlock):
            raise InvalidTypeException("Expected a Basic Block")

        branch_inst = BranchInstruction(bb, self.__current_bb, name)
        self.__add_instruction(branch_inst)
        return branch_inst

    def create_cond_branch(self, cmp_inst, value, bb_true, bb_false, name=None):
        cond_branch = ConditionalBranchInstruction(cmp_inst, value, bb_true, bb_false, self.__current_bb, name)
        self.__add_instruction(cond_branch)
        return cond_branch

    def create_call(self, func, args, name=None):
        call_inst = CallInstruction(func, args, self.__current_bb, name)
        self.__add_instruction(call_inst)
        return call_inst

    def create_add(self, lhs, rhs, name=None):
        folded_inst = self.const_fold_binary_op(lhs, rhs, '+')
        if folded_inst is not None:
            return folded_inst

        add_inst = AddInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(add_inst)
        return add_inst

    def create_sub(self, lhs, rhs, name=None):
        folded_inst = self.const_fold_binary_op(lhs, rhs, '-')
        if folded_inst is not None:
            return folded_inst

        sub_inst = SubInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(sub_inst)
        return sub_inst

    def create_mul(self, lhs, rhs, name=None):
        folded_inst = self.const_fold_binary_op(lhs, rhs, '*')
        if folded_inst is not None:
            return folded_inst

        mul_inst = MulInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(mul_inst)
        return mul_inst

    def create_div(self, lhs, rhs, name=None):
        folded_inst = self.const_fold_binary_op(lhs, rhs, '/')
        if folded_inst is not None:
            return folded_inst

        div_inst = DivInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(div_inst)
        return div_inst

    def create_icmp(self, lhs, rhs, comparator, name=None):
        icmp_inst = ICmpInstruction(CompareTypes.SLE, lhs, rhs, self.__current_bb, name)
        self.__add_instruction(icmp_inst)
        return icmp_inst

    def create_select(self, cond, val_true, val_false, name=None):
        select_inst = SelectInstruction(cond, val_true, val_false, self.__current_bb, name)
        self.__add_instruction(select_inst)
        return select_inst

    def create_alloca(self, numEls=None, name=None):
        alloca_inst = AllocaInstruction(numEls, self.__current_bb, name)
        self.__add_instruction(alloca_inst)
        return alloca_inst

    def create_load(self, alloca):
        load_inst = LoadInstruction(alloca, parent=self.__current_bb)
        self.__add_instruction(load_inst)
        return load_inst

    def create_store(self, alloca, value):
        store_inst = StoreInstruction(alloca, value, parent=self.__current_bb)
        self.__add_instruction(store_inst)
        return store_inst

    def create_shl(self, op1, op2, name=None):
        folded_inst = self.const_fold_binary_op(op1, op2, '<<')
        if folded_inst is not None:
            return folded_inst

        shl_inst = ShiftLeftInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(shl_inst)
        return shl_inst

    def create_lshr(self, op1, op2, name=None):
        folded_inst = self.const_fold_binary_op(op1, op2, '>>')
        if folded_inst is not None:
            return folded_inst

        lshr_inst = LogicalShiftRightInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(lshr_inst)
        return lshr_inst

    def create_ashr(self, op1, op2, name=None):
        ashr_inst = ArithmeticShiftRightInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(ashr_inst)
        return ashr_inst

    def create_and(self, op1, op2, name=None):
        folded_inst = self.const_fold_binary_op(op1, op2, '&')
        if folded_inst is not None:
            return folded_inst

        and_inst = AndInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(and_inst)
        return and_inst

    def create_or(self, op1, op2, name=None):
        folded_inst = self.const_fold_binary_op(op1, op2, '|')
        if folded_inst is not None:
            return folded_inst

        or_inst = OrInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(or_inst)
        return or_inst

    def create_xor(self, op1, op2, name=None):
        folded_inst = self.const_fold_binary_op(op1, op2, '^')
        if folded_inst is not None:
            return folded_inst

        xor_inst = XorInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(xor_inst)
        return xor_inst

    def create_number(self, number):
        number = Number(number)
        return number

    def create_string(self, string):
        string_obj = String(string)
        return string_obj

    #def create_vector(self, baseTy, numElts, name=None):
    #    vecTy = VectorType(baseTy, numElts)
    #    alloca = self.create_alloca(vecTy, 1, None, name)
    #    vec = self.create_load(alloca)
    #    return vec