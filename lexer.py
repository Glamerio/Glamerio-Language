import re

# A simple lexer for a hypothetical programming language
# This lexer tokenizes a small set of keywords, identifiers, numbers, strings, and operators.

TOKENS = [
    # Keywords
    ('KEYWORD', r'\b(fn|if|else|for|while|class|return|input|print|this)\b'),

    # Data types
    ('TYPE', r'\b(int|float|str|bool)\b'),

    # Boolean & null values
    ('BOOL', r'\b(True|False)\b'),
    ('NULL', r'\bnull\b'),

    # Identifiers (variables, function names, etc.)
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # Numbers (integers and floats)
    ('NUMBER', r'\d+(\.\d+)?'),

    # Strings
    ('STRING', r'"[^"\n]*"'),

    # Symbols
    ('SEMI', r';'),
    ('COMMA', r','),
    ('DOT', r'\.'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    
    # Operators
    ('OP', r'\^|==|!=|<=|>=|=|<|>|\+|\-|\*|\/'),


    # Whitespace and comments (ignored)
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('COMMENT', r'\#.*')
]

# Compile all regexes into a single pattern
TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS))

# Lexer function
def lexer(code):
    tokens = []
    for match in TOKEN_RE.finditer(code):
        kind = match.lastgroup
        value = match.group()

        # Skip whitespace, newlines, and comments
        if kind in ('NEWLINE', 'SKIP', 'COMMENT'):
            continue

        # Remove quotes from strings
        if kind == 'STRING':
            value = value[1:-1]

        tokens.append((kind, value))

    return tokens

# Example usage: run with test file
if __name__ == "__main__":
    try:
        with open('program.gl', 'r', encoding='utf-8') as f:
            code = f.read()
        token_list = lexer(code)
        for token in token_list:
            print(token)
    except FileNotFoundError:
        print("Error: 'program.gl' file not found.")