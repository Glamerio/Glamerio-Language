from lexer import lexer
from parser import parse_program, print_ast
from interpreter import run

with open("program.gl", "r", encoding="utf-8") as f:
    code = f.read()

tokens = lexer(code)
ast = parse_program(tokens)
run(ast)