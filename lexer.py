import re

# A simple lexer for a hypothetical programming language
# This lexer tokenizes a small set of keywords, identifiers, numbers, strings, and operators.

TOKENS = [
    # Keywords
    ('KEYWORD', r'\b(fn|if|else|for|while|class|return|input|print|this)\b'),

    # Data types
    ('TYPE', r'\b(int|float|string|bool)\b'),

    # Boolean & null values
    ('BOOL', r'\b(True|False)\b'),
    ('NULL', r'\bNull\b'),

    # Identifiers (variables, function names, etc.)
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # Numbers (int or float)
    ('NUMBER', r'\d+(\.\d+)?'),

    # Strings
    ('STRING', r'"[^"\n]*"'),

    # Operators
    ('OP', r'==|!=|<=|>=|=|<|>|\+|\-|\*|\/'),

    # Symbols
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('SEMI', r';'),
    ('COMMA', r','),
    ('DOT', r'\.'),

    # Whitespace and comments
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('COMMENT', r'\#.*')
]
# Compile the regular expressions for each token type
TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in TOKENS))

# Lexer function that takes a string of code and returns a list of tokens
def lexer(code):
    tokens = []
    for mo in TOKEN_RE.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ('NEWLINE', 'SKIP', 'COMMENT'):
            continue
        elif kind == 'STRING':
            value  = value[1:-1] # remove quotes
        tokens.append((kind, value))
    return tokens

# Example usage:
if __name__ == "__main__":
    with open('program.gl', 'r') as f:
        code = f.read()
    token_list = lexer(code)
    for token in token_list:
        print(token)
# Example code to test the lexer