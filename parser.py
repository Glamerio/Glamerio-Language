from lexer import lexer  # Import lexer function

# ----------------------
# Token Stream Class
# ----------------------
class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, expected_type=None):
        token = self.peek()
        if token is None:
            raise Exception("Unexpected end of input")
        if expected_type and token[0] != expected_type:
            raise Exception(f"Expected token type {expected_type}, but got {token[0]}")
        self.position += 1
        return token


# ----------------------
# AST Node Definitions
# ----------------------
class VarDeclarationNode:
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

class PrintNode:
    def __init__(self, value):
        self.value = value

class LiteralNode:
    def __init__(self, value):
        self.value = value

class StringNode:
    def __init__(self, value):
        self.value = value

class IdentifierNode:
    def __init__(self, name):
        self.name = name        

class BinaryOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class InputNode:
    def __init__(self, prompt):
        self.prompt = prompt

class IfNode:
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class BlockNode:
    def __init__(self, statements):
        self.statements = statements

class FunctionDefNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ReturnNode:
    def __init__(self, value):
        self.value = value

# ----------------------
# Expression Parsers (with precedence)
# ----------------------

# Lowest precedence: + -
def parse_expression(stream):
    left = parse_term(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] in ('+', '-'):
        op = stream.consume()[1]
        right = parse_term(stream)
        left = BinaryOpNode(left, op, right)
    return left

# Medium precedence: * /
def parse_term(stream):
    left = parse_power(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] in ('*', '/'):
        op = stream.consume()[1]
        right = parse_power(stream)
        left = BinaryOpNode(left, op, right)
    return left

# High precedence: ^
# RIGHT-associative: a ^ b ^ c → a ^ (b ^ c)
def parse_power(stream):
    left = parse_factor(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '^':
        op = stream.consume()[1]
        right = parse_power(stream)  # right-associative
        left = BinaryOpNode(left, op, right)
    return left

# Highest level: numbers, identifiers, parentheses
def parse_factor(stream):
    token = stream.peek()
    if token[0] == 'LPAREN':
        stream.consume('LPAREN')
        expr = parse_expression(stream)
        stream.consume('RPAREN')
        return expr
    elif token[0] == 'NUMBER':
        return LiteralNode(stream.consume()[1])
    elif token[0] == 'STRING':
        return StringNode(stream.consume()[1])
    elif token[0] == 'ID':
        return IdentifierNode(stream.consume()[1])
    else:
        raise Exception(f"Invalid factor: {token}")


# ----------------------
# Other Statements
# ----------------------
def parse_variable_declaration(stream):
    var_type = stream.consume('TYPE')[1]
    var_name = stream.consume('ID')[1]
    stream.consume('OP')  # Expect '='
    value = parse_expression(stream)
    stream.consume('SEMI')  # Expect ';'
    return VarDeclarationNode(var_type, var_name, value)

def parse_print_statement(stream):
    stream.consume('KEYWORD')  # 'print'
    stream.consume('LPAREN')
    value = parse_expression(stream)
    stream.consume('RPAREN')
    stream.consume('SEMI')
    return PrintNode(value)

def parse_input_statement(stream):
    stream.consume('KEYWORD')  # 'input'
    stream.consume('LPAREN')
    prompt = parse_expression(stream)
    stream.consume('RPAREN')
    stream.consume('SEMI')
    return InputNode(prompt)

def parse_if_statement(stream):
    stream.consume('KEYWORD')  # 'if'
    stream.consume('LPAREN')
    condition = parse_expression(stream)
    stream.consume('RPAREN')
    then_block = parse_block(stream)

    else_block = None
    if stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'else':
        stream.consume('KEYWORD')  # 'else'
        else_block = parse_block(stream)

    return IfNode(condition, then_block, else_block)

def parse_while_statement(stream):
    stream.consume('KEYWORD')  # 'while'
    stream.consume('LPAREN')
    condition = parse_expression(stream)
    stream.consume('RPAREN')
    body = parse_block(stream)
    return WhileNode(condition, body)

def parse_function_definition(stream):
    stream.consume('KEYWORD')  # 'fn'
    name = stream.consume('ID')[1]
    stream.consume('LPAREN')

    params = []
    if stream.peek()[0] != 'RPAREN':
        while True:
            param = stream.consume('ID')[1]
            params.append(param)
            if stream.peek()[0] == 'COMMA':
                stream.consume('COMMA')
            else:
                break

    stream.consume('RPAREN')
    body = parse_block(stream)
    return FunctionDefNode(name, params, body)

def parse_return_statement(stream):
    stream.consume('KEYWORD')  # 'return'
    value = parse_expression(stream)
    stream.consume('SEMI')
    return ReturnNode(value)

def parse_function_call(stream):
    name = stream.consume('ID')[1]
    stream.consume('LPAREN')

    args = []
    if stream.peek()[0] != 'RPAREN':
        while True:
            arg = parse_expression(stream)
            args.append(arg)
            if stream.peek()[0] == 'COMMA':
                stream.consume('COMMA')
            else:
                break

    stream.consume('RPAREN')
    stream.consume('SEMI')
    return FunctionCallNode(name, args)

# ----------------------
# Block Parser
# ----------------------
def parse_block(stream):
    stream.consume('LBRACE')
    statements = []
    while stream.peek() and stream.peek()[0] != 'RBRACE':
        token = stream.peek()
        if token[0] == 'TYPE':
            node = parse_variable_declaration(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'print':
            node = parse_print_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'input':
            node = parse_input_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'if':
            node = parse_if_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'while':
            node = parse_while_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'return':
            node = parse_return_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'fn':
            node = parse_function_definition(stream)
            statements.append(node)
        elif token[0] == 'ID' and stream.tokens[stream.position+1][0] == 'LPAREN':
            node = parse_function_call(stream)
            statements.append(node)
        else:
            raise Exception(f"Unexpected token in block: {token}")
    stream.consume('RBRACE')
    return BlockNode(statements)

# ----------------------
# Top-Level Program Parser
# ----------------------
def parse_program(tokens):
    stream = TokenStream(tokens)
    ast_nodes = []

    while stream.peek():
        token = stream.peek()
        if token[0] == 'TYPE':
            node = parse_variable_declaration(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'print':
            node = parse_print_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'input':
            node = parse_input_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'if':
            node = parse_if_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'while':
            node = parse_while_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'return':
            node = parse_return_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'fn':
            node = parse_function_definition(stream)
            ast_nodes.append(node)
        elif token[0] == 'ID' and stream.tokens[stream.position+1][0] == 'LPAREN':
            node = parse_function_call(stream)
            ast_nodes.append(node)
        else:
            raise Exception(f"Unexpected token: {token}")

    return ast_nodes


# ----------------------
# AST Printer (for debugging)
# ----------------------
def print_ast(node):
    if isinstance(node, LiteralNode):
        return node.value
    elif isinstance(node, IdentifierNode):
        return node.name
    elif isinstance(node, StringNode):
        return f'"{node.value}"'
    elif isinstance(node, BinaryOpNode):
        return f"({print_ast(node.left)} {node.operator} {print_ast(node.right)})"
    elif isinstance(node, VarDeclarationNode):
        return f"{node.var_type} {node.name} = {print_ast(node.value)};"
    elif isinstance(node, PrintNode):
        return f"print({print_ast(node.value)});"
    else:
        return str(node)