__author__ = 'sarangis'

from ir.types import *
from ir.function import *
from ir.context import *
from ir.module import *
from ir.instructions import *

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

    def create_function_type(self, ret_ty, *arg_tys):
        return FunctionType(ret_ty, *arg_tys)

    @verify(name=str, ftype=FunctionType)
    def create_function(self, name, ftype, *args):
        f = Function(name, ftype)
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

    def create_call(self, func, *args, name=None):
        call_inst = CallInstruction(func, list(args), self.__current_bb, name)
        self.__add_instruction(call_inst)
        return call_inst

    def create_add(self, lhs, rhs, name=None):
        add_inst = AddInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(add_inst)
        return add_inst

    def create_sub(self, lhs, rhs, name=None):
        sub_inst = SubInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(sub_inst)
        return sub_inst

    def create_mul(self, lhs, rhs, name=None):
        mul_inst = MulInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(mul_inst)
        return mul_inst

    def create_div(self, lhs, rhs, name=None):
        div_inst = DivInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(div_inst)
        return div_inst

    def create_fadd(self, lhs, rhs, name=None):
        fadd_inst = FAddInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(fadd_inst)
        return fadd_inst

    def create_fsub(self, lhs, rhs, name=None):
        fsub_inst = FSubInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(fsub_inst)
        return fsub_inst

    def create_fmul(self, lhs, rhs, name=None):
        fmul_inst = FMulInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(fmul_inst)
        return fmul_inst

    def create_fdiv(self, lhs, rhs, name=None):
        fdiv_inst = FDivInstruction(lhs, rhs, self.__current_bb, name)
        self.__add_instruction(fdiv_inst)
        return fdiv_inst

    def create_icmp(self, lhs, rhs, name=None):
        icmp_inst = ICmpInstruction(CompareTypes.SLE, lhs, rhs, self.__current_bb, name)
        self.__add_instruction(icmp_inst)
        return icmp_inst

    def create_select(self, cond, val_true, val_false, name=None):
        select_inst = SelectInstruction(cond, val_true, val_false, self.__current_bb, name)
        self.__add_instruction(select_inst)
        return select_inst

    def create_alloca(self, type, numEls=None, align=None, name=None):
        alloca_inst = AllocaInstruction(type, numEls, align, self.__current_bb, name)
        self.__add_instruction(alloca_inst)
        return alloca_inst

    def create_load(self):
        pass

    def create_store(self):
        pass

    def create_shl(self, op1, op2, name=None):
        shl_inst = ShiftLeftInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(shl_inst)
        return shl_inst

    def create_lshr(self, op1, op2, name=None):
        lshr_inst = LogicalShiftRightInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(lshr_inst)
        return lshr_inst

    def create_ashr(self, op1, op2, name=None):
        ashr_inst = ArithmeticShiftRightInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(ashr_inst)
        return ashr_inst

    def create_and(self, op1, op2, name=None):
        and_inst = AndInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(and_inst)
        return and_inst

    def create_or(self, op1, op2, name=None):
        or_inst = OrInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(or_inst)
        return or_inst

    def create_xor(self, op1, op2, name=None):
        xor_inst = XorInstruction(op1, op2, self.__current_bb, name)
        self.__add_instruction(xor_inst)
        return xor_inst

    def create_vector(self, baseTy, numElts, name=None):
        vecTy = VectorType(baseTy, numElts)
        alloca = self.create_alloca(vecTy, 1, None, name)
        vec = self.create_load(alloca)
        return vec