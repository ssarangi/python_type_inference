class BaseVisitor(object):
    def __init__(self):
        pass

    def visit(self, node, *args):
        name = "visit_%s" % type(node).__name__.lower()
        if hasattr(self, name):
            return getattr(self, name)(node, *args)
        else:
            return self.generic_visit(node)

    def generic_visit(self, node):
        raise NotImplementedError("Visitor class doesn't implement visit_%s" % type(node).__name__)

class IRBaseVisitor(BaseVisitor):
    def __init__(self):
        BaseVisitor.__init__(self)
        pass

    def visit_module(self, node):
        pass

    def visit_function(self, node, arg_list):
        pass

    def visit_callinstruction(self, node):
        pass

    def visit_terminateinstruction(self, node):
        pass

    def visit_returninstruction(self, node):
        pass

    def visit_selectinstruction(self, node):
        pass

    def visit_loadinstruction(self, node):
        pass

    def visit_storeinstruction(self, node):
        pass

    def visit_addinstruction(self, node):
        pass

    def visit_subinstruction(self, node):
        pass

    def visit_mulinstruction(self, node):
        pass

    def visit_divinstruction(self, node):
        pass

    def visit_allocainstruction(self, node):
        pass

    def visit_phiinstruction(self, node):
        pass

    def visit_conditionalbranchinstruction(self, node):
        pass

    def visit_indirectbranchinstruction(self, node):
        pass

    def visit_switchinstruction(self, node):
        pass

    def visit_icmpinstruction(self, node):
        pass

    def visit_fcmpinstruction(self, node):
        pass

    def visit_castinstruction(self, node):
        pass

    def visit_gepinstruction(self, node):
        pass

    def visit_extractelementinstruction(self, node):
        pass

    def visit_insertelementinstruction(self, node):
        pass

    def visit_shiftleftinstruction(self, node):
        pass

    def visit_logicalshiftrightinstruction(self, node):
        pass

    def visit_arithmeticshiftrightinstruction(self, node):
        pass

    def visit_andinstruction(self, node):
        pass

    def visit_orinstruction(self, node):
        pass

    def visit_xorinstruction(self, node):
        pass

    def visit_basicblock(self, node):
        pass