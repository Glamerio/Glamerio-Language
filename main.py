import sys
from lexer import lexer
from parser import parse_program
from interpreter import run

if len(sys.argv) < 2:
    print("Kullanım: python main.py <kaynak_dosyası>")
    sys.exit(1)

filename = sys.argv[1]
with open(filename, "r", encoding="utf-8") as f:
    code = f.read()

tokens = lexer(code)
ast = parse_program(tokens)

run(ast)