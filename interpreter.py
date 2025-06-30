# ---------------------------------------------
# Glamerio Interpreter - interpreter.py
# Full runtime support for:
# - Variables, Print, Input
# - If / Else, While
# - Functions, Return
# ---------------------------------------------

from parser import (
    LiteralNode, StringNode, IdentifierNode, BinaryOpNode,
    VarDeclarationNode, PrintNode, InputNode, IfNode,
    WhileNode, BlockNode, FunctionDefNode, FunctionCallNode,
    ReturnNode
)

memory = {}         # global variables
functions = {}      # function definitions
call_stack = []     # for function calls

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


def evaluate(node, local_scope=None):
    scope = local_scope if local_scope is not None else memory

    if isinstance(node, LiteralNode):
        value = node.value
        return float(value) if '.' in value else int(value)

    elif isinstance(node, StringNode):
        return node.value

    elif isinstance(node, IdentifierNode):
        name = node.name
        if name in scope:
            return scope[name]
        elif name in memory:
            return memory[name]
        else:
            raise Exception(f"Undefined variable: {name}")

    elif isinstance(node, BinaryOpNode):
        left = evaluate(node.left, scope)
        right = evaluate(node.right, scope)
        op = node.operator
        if op == '+': return left + right
        elif op == '-': return left - right
        elif op == '*': return left * right
        elif op == '/': return left / right
        elif op == '^': return left ** right
        elif op == '==': return left == right
        elif op == '!=': return left != right
        elif op == '<': return left < right
        elif op == '<=': return left <= right
        elif op == '>': return left > right
        elif op == '>=': return left >= right
        else: raise Exception(f"Unknown operator: {op}")

    elif isinstance(node, VarDeclarationNode):
        value = evaluate(node.value, scope)
        scope[node.name] = value

    elif isinstance(node, PrintNode):
        value = evaluate(node.value, scope)
        print(value)

    elif isinstance(node, InputNode):
        prompt = evaluate(node.prompt, scope)
        return input(prompt)

    elif isinstance(node, IfNode):
        condition = evaluate(node.condition, scope)
        if condition:
            evaluate(node.then_block, scope)
        elif node.else_block:
            evaluate(node.else_block, scope)

    elif isinstance(node, WhileNode):
        while evaluate(node.condition, scope):
            evaluate(node.body, scope)

    elif isinstance(node, BlockNode):
        for stmt in node.statements:
            evaluate(stmt, scope)

    elif isinstance(node, FunctionDefNode):
        functions[node.name] = node  # store the function definition

    elif isinstance(node, FunctionCallNode):
        func = functions.get(node.name)
        if not func:
            raise Exception(f"Function '{node.name}' not defined")
        # Create local scope for function
        local = {}
        for i, param in enumerate(func.params):
            local[param] = evaluate(node.args[i], scope)
        try:
            evaluate(func.body, local)
        except ReturnException as r:
            return r.value

    elif isinstance(node, ReturnNode):
        value = evaluate(node.value, scope)
        raise ReturnException(value)

    else:
        raise Exception(f"Unknown node type: {type(node)}")


def run(ast):
    for node in ast:
        evaluate(node)