__author__ = 'sarangis'

class ModulePass:
    def __init__(self):
        pass

    def run_on_module(self, node):
        raise NotImplementedError("Derived passes class should implement run_on_module")

class FunctionPass:
    def __init__(self):
        pass

    def run_on_function(self, node):
        raise NotImplementedError("Derived passes class should implement run_on_function")


class InstVisitorPass:
    def __init__(self):
        pass

    def visit(self, node):
        name = "visit_%s" % type(node).__name__.lower()
        if hasattr(self, name):
            return getattr(self, name)(node)
        else:
            return self.generic_visit(node)

    def generic_visit(self, node):
        raise NotImplementedError("Generic Visitor not implemented")

    def visit_module(self, node):
        # Iterate through all the functions in the module
        results = [self.visit_function(f) for f in node.functions]
        return results

    def visit_function(self, node):
        # Iterate through all the basic blocks in the module
        results = [self.visit_basicblock(bb) for bb in node.basic_blocks]
        return results

    def visit_basicblock(self, node):
        # Iterate through all the instructions in the module
        results = [self.visit(i) for i in node.instructions]
        return results

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

    def visit_faddinstruction(self, node):
        pass

    def visit_fsubinstruction(self, node):
        pass

    def visit_fmulinstruction(self, node):
        pass

    def visit_fdivinstruction(self, node):
        pass

    def visit_allocainstruction(self, node):
        pass

    def visit_phiinstruction(self, node):
        pass

    def visit_branchinstruction(self, node):
        pass

    def visit_conditionalbranchinstruction(self, node):
        pass

    def visit_indirectbranchinstruction(self, node):
        pass

    def visit_switchinstruction(self, node):
        pass

    def visit_selectinstruction(self, node):
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