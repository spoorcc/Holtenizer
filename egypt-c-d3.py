#!/usr/bin/env python

import sys
from pycparser import c_parser, c_ast, parse_file
import json


class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.caller = None
        self.call_dict = {}

    def visit_FuncDef(self, node):
        self.caller = node.decl.name

        for name, child in node.children():
            self.visit(child)

    def visit_FuncCall(self, node):

        called_func = filename + '.' + node.name.name

        try:
            self.call_dict[self.caller]['imports'] += [called_func]
        except KeyError:
            self.call_dict[self.caller] = {'name': filename + '.' + self.caller,
                                           'size':1,
                                           'imports': [called_func]}

        self._add_called_func_to_dict(called_func)

    def _add_called_func_to_dict(self, funcname):

        if funcname not in self.call_dict.keys():
            self.call_dict[funcname] = {'name': funcname,
                                        'size':1,
                                        'imports': []}

def show_func_calls(filename):
    ast = parse_file(filename, use_cpp=True,
                     cpp_path='gcc',
                     cpp_args=['-E', r'-Ipycparser/utils/fake_libc_include'])

    v = FuncCallVisitor()
    v.visit(ast)

    print(json.dumps(v.call_dict.values(), sort_keys=True, indent=4))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    show_func_calls(filename)
