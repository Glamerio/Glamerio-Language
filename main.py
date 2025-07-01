from lexer import lexer
from parser import parse_program, print_ast
from interpreter import run

with open("test_cases.gl", "r", encoding="utf-8") as f:
    code = f.read()

tokens = lexer(code)
ast = parse_program(tokens)

# with open("tokens.txt", "w", encoding="utf-8") as f:
#     for token in tokens:
#         f.write(f"{token}\n")

run(ast)