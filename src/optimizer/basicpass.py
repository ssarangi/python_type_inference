__author__ = 'sarangis'

from optimizer.pass_support import *
from ir.validator import *
from ir.module import *
from ir.function import *

class PrintFunctionsPass(ModulePass):
    def __init__(self):
        ModulePass.__init__(self)

    @verify(node=Module)
    def run_on_module(self, node):
        print()
        print("Functions List:")
        print("-" * 50)
        for f in node.functions:
            print(f.name)


class PrintBasicBlocksPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)

    @verify(node=Function)
    def run_on_function(self, node):
        print()
        print("Function: %s" % node.name)
        print("Basic Block List:")
        print("-" * 50)
        for bb in node.basic_blocks:
            print(bb.name)

class PrintInstructionUsesPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)

    @verify(node=Function)
    def run_on_function(self, node):
        for bb in node.basic_blocks:
            for inst in bb.instructions:
                print("-" * 50 + " Uses " + "-" * 50 + "\n")
                print(str(inst))
                for use in inst.uses:
                    print(" ==> " + str(use))


class DominatorTree:
    def __init__(self, dom_tree):
        self.__dom = dom_tree

    def dominates(self, node1, node2):
        dom = list(self.__dom[node1])
        if node2 in dom:
            return True
        else:
            return False

    def strictly_dominators(self, node1, node2):
        if self.dominates(node1, node2):
            if node1 != node2:
                return True
            else:
                return False

class DominatorTreeAnalysisPass(FunctionPass):
    def __init__(self):
        FunctionPass.__init__(self)
        self.__postorder = []
        self.__dominator_tree = None

    @property
    def dominator_tree(self):
        return self.__dominator_tree

    def dfs(self, node, marked, pre, post, precounter, postcounter):
        marked[node] = True
        pre[node] = precounter
        self.__postorder.append(node)
        precounter += 1
        for succ in node.successors:
            if succ not in marked:
                pre, post, precounter, postcounter = self.dfs(succ, marked, pre, post, precounter, postcounter)

        post[node] = postcounter
        postcounter += 1
        return pre, post, precounter, postcounter

    @verify(node=Function)
    def run_on_function(self, node):
        entry_bb = node.basic_blocks[0]

        dom = {}
        final_dom = {}
        self.dfs(entry_bb, {}, {}, {}, 0, len(node.basic_blocks))

        for bb in node.basic_blocks:
            dom[bb] = set(node.basic_blocks)
            final_dom[bb] = set(node.basic_blocks)

        changed = True
        while changed:
            changed = False
            for bb in self.__postorder:
                final_dom[bb] = set(bb.predecessors)
                for pred in bb.predecessors:
                    final_dom[bb].intersection(dom[pred])
                    if final_dom[bb] != dom[bb]:
                        dom[bb] = final_dom[bb]
                        changed = True

        self.__dominator_tree = DominatorTree(final_dom)