from ir.module import *
from ir.function import *
from ir.instructions import *

from ir.base_ir_visitor import *
from ir.validator import *

import operator
from collections import deque

COMPARE_OPERATORS = {
    CompareTypes.SLT: operator.lt,
    CompareTypes.SLE: operator.le,
    CompareTypes.EQ:  operator.eq,
    CompareTypes.NE:  operator.ne,
    CompareTypes.SGT: operator.gt,
    CompareTypes.SGE: operator.ge,
}

BITWISE_BINARY_OPERATORS = {
    BitwiseBinaryInstruction.SHL: operator.ilshift,
    BitwiseBinaryInstruction.ASHR: operator.irshift,
    BitwiseBinaryInstruction.LSHR: operator.rshift,
    BitwiseBinaryInstruction.AND: operator.iand,
    BitwiseBinaryInstruction.OR: operator.ior,
    BitwiseBinaryInstruction.XOR: operator.xor,
}

class Frame:
    def __init__(self, name):
        self.__symbols = {}
        self.__name = name

    @property
    def name(self):
        return self.__name

    def add_to_frame(self, node, value):
        self.__symbols[node] = value

    def get_symbol(self, node):
        if isinstance(node, Constant):
            return node.initializer

        if node in self.__symbols:
            val = self.__symbols[node]
            if isinstance(val, Constant):
                return val.initializer
            else:
                return val
        else:
            raise Exception("No symbol found")
        
        return None

class IRVirtualMachine(IRBaseVisitor):
    def __init__(self):
        IRBaseVisitor.__init__(self)
        self.__global_frame = Frame("module")
        self.__frames = []
        self.__ip = None
        self.__result_stack = deque([])
        self.__current_frame = None

    @property
    def eval_result(self):
        assert len(self.__result_stack) > 0 and len(self.__result_stack) < 2
        return self.__result_stack.popleft()

    def visit_module(self, node):
        self.__current_frame = self.__global_frame
        for g in node.globals:
            self.__global_frame.add_to_frame(g, g.initializer)

        # At this point we don't have support for system arguments
        self.visit(node.entry_point, [])

    # @verify(node=Function, arg_list=list)
    def visit_function(self, node, arg_list):
        frame = Frame(node.name)

        assert len(node.args) == len(arg_list), "args passed is of incorrect size"
        # Iterate through the args and set the values
        for idx, arg in enumerate(node.args):
            frame.add_to_frame(arg, arg_list[idx])

        # Find the first basic block and move there
        self.__ip = node.basic_blocks[0]

        if self.__current_frame is not None:
            self.__frames.append(self.__current_frame)

        self.__current_frame = frame
        self.visit(self.__ip)

    @verify(node=BasicBlock)
    def visit_basicblock(self, node):
        for inst in node.instructions:
            self.visit(inst)

    def visit_callinstruction(self, node):
        sym_args = [self.__current_frame.get_symbol(arg) for arg in node.args]
        self.visit(node.function, sym_args)
        assert len(self.__result_stack) > 0
        self.__current_frame.add_to_frame(node, self.__result_stack.popleft())

    def visit_terminateinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_returninstruction(self, node):
        val = node.value
        val_sym = self.__current_frame.get_symbol(val)
        self.__result_stack.append(val_sym)
        self.__current_frame = self.__frames.pop()

    def visit_selectinstruction(self, node):
        condition = node.condition
        val_true = node.val_true
        val_false = node.val_false

        condition_sym = self.__current_frame.get_symbol(condition)

        if condition_sym is True:
            val_true_sym = self.__current_frame.get_symbol(val_true)
            self.__current_frame.add_to_frame(node, val_true_sym)
        else:
            val_false_sym = self.__current_frame.get_symbol(val_false)
            self.__current_frame.add_to_frame(node, val_false_sym)

    def visit_loadinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_storeinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_binop(self, op, node):
        lhs = node.lhs
        rhs = node.rhs

        lhs_sym = self.__current_frame.get_symbol(lhs)
        rhs_sym = self.__current_frame.get_symbol(rhs)

        res = op(lhs_sym, rhs_sym)
        self.__current_frame.add_to_frame(node, res)

    def visit_addinstruction(self, node):
        self.visit_binop(operator.add, node)

    def visit_subinstruction(self, node):
        self.visit_binop(operator.sub, node)

    def visit_mulinstruction(self, node):
        self.visit_binop(operator.mul, node)

    def visit_divinstruction(self, node):
        self.visit_binop(operator.floordiv, node)

    def visit_faddinstruction(self, node):
        self.visit_binop(operator.add, node)

    def visit_fsubinstruction(self, node):
        self.visit_binop(operator.sub, node)

    def visit_fmulinstruction(self, node):
        self.visit_binop(operator.mul, node)

    def visit_fdivinstruction(self, node):
        self.visit_binop(operator.truediv, node)

    def visit_allocainstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_phiinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_conditionalbranchinstruction(self, node):
        cmp_inst = node.cmp_inst
        cmp_val = node.cmp_value
        bb_true = node.bb_true
        bb_false = node.bb_false

        cmp_res = self.__current_frame.get_symbol(cmp_inst)
        if cmp_res == cmp_val:
            self.__ip = bb_true
        else:
            self.__ip = bb_false

        self.visit(self.__ip)

    def visit_indirectbranchinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_switchinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    # @verify(node=ICmpInstruction)
    def visit_icmpinstruction(self, node):
        cond = node.condition
        op1 = node.op1
        op2 = node.op2

        # find the symbols from the node
        val1 = self.__current_frame.get_symbol(op1)
        val2 = self.__current_frame.get_symbol(op2)

        val = COMPARE_OPERATORS[cond](val1, val2)
        self.__current_frame.add_to_frame(node, val)

    def visit_fcmpinstruction(self, node):
        # Just call the icmp version itself since python doesn't distinguish between int and floats
        # for compare operators
        self.visit_icmpinstruction(node)

    def visit_castinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_gepinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_extractelementinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_insertelementinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_bitwise_binop(self, op, node):
        op1 = node.op1
        op2 = node.op2

        op1_sym = self.__current_frame.get_symbol(op1)
        op2_sym = self.__current_frame.get_symbol(op2)

        res = op(op1_sym, op2_sym)
        self.__current_frame.add_to_frame(node, res)

    def visit_shiftleftinstruction(self, node):
        self.visit_bitwise_binop(operator.ilshift, node)

    def visit_logicalshiftrightinstruction(self, node):
        self.visit_bitwise_binop(operator.rshift, node)

    def visit_arithmeticshiftrightinstruction(self, node):
        self.visit_bitwise_binop(operator.irshift, node)

    def visit_andinstruction(self, node):
        self.visit_bitwise_binop(operator.iand, node)

    def visit_orinstruction(self, node):
        self.visit_bitwise_binop(operator.ior, node)

    def visit_xorinstruction(self, node):
        self.visit_xorinstruction(operator.ixor, node)