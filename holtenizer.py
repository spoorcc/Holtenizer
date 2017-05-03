#!/usr/bin/env python

import sys
from pycparser import c_parser, c_ast, parse_file
import json
import os.path
from os import sep as os_sep

class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self, filename):
        self.caller = None
        self.call_dict = {}
        self.func_defs = []
        self.file_prefix = self._create_file_prefix(filename)

    @staticmethod
    def _create_file_prefix(filename):
        name, _ = os.path.splitext(filename)
        return name.replace(os_sep, '.')

    def visit_FuncDef(self, node):
        self.caller = self.file_prefix + '.' + node.decl.name

        self.func_defs += [self.caller]

        for name, child in node.children():
            self.visit(child)

    def visit_FuncCall(self, node):

        called_func = node.name.name

        try:
            self.call_dict[self.caller]['imports'] += [called_func]
        except KeyError:
            self.call_dict[self.caller] = {'name': self.caller,
                                           'size':1,
                                           'imports': [called_func]}

def replace_funcs_with_known_funcs(call_dict, func_defs):

    undeffed_func = []

    # TODO: Naive implementation, replace with suffix array?
    for function, function_call_list in call_dict.items():
        for called_func in function_call_list['imports']:
            for defined_function in func_defs:
                if defined_function.split('.')[-1] == called_func:
                    call_dict[function]['imports'] = [defined_function if call == called_func else call for call in call_dict[function]['imports']]
                    break
            else:
                undeffed_func += [called_func]

    for called_func in undeffed_func:
        call_dict[called_func] = {'name': called_func,
                                  'size':1,
                                  'imports': []}
    return call_dict

def show_func_calls(filename):
    ast = parse_file(filename, use_cpp=True,
                     cpp_path='gcc',
                     cpp_args=['-E', r'-Ipycparser/utils/fake_libc_include'])

    v = FuncCallVisitor(filename)
    v.visit(ast)

    call_dict = replace_funcs_with_known_funcs(v.call_dict, v.func_defs)

    print(json.dumps(list(call_dict.values()), sort_keys=True, indent=4))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    show_func_calls(filename)
