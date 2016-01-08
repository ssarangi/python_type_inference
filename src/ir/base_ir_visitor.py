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
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_function(self, node, arg_list):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_callinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_terminateinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_returninstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_selectinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_loadinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_storeinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_addinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())
    
    def visit_subinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_mulinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_divinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_faddinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_fsubinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_fmulinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_fdivinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_allocainstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_phiinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_conditionalbranchinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_indirectbranchinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_switchinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())
    
    def visit_selectinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_icmpinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_fcmpinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_castinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_gepinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_extractelementinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_insertelementinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_shiftleftinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_logicalshiftrightinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_arithmeticshiftrightinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_andinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_orinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_xorinstruction(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())

    def visit_basicblock(self, node):
        raise NotImplementedError("IR Node not implemented: visit_%s" % type(node).__name__.lower())