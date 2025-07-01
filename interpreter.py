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
    ReturnNode,ForNode
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
        if value == 'null':
            return None
        elif value == 'True':
            return True
        elif value == 'False':
            return False
        return float(value) if '.' in value else int(value)

    elif isinstance(node, StringNode):
        return node.value
    
    elif isinstance(node, InputNode):
        prompt = evaluate(node.prompt, scope)
        return input(str(prompt))  # Ensure it's string prompt

    elif isinstance(node, IdentifierNode):
        name = node.name
        if name in scope:
            return scope[name]
        elif name in memory:
            return memory[name]
        else:
            raise Exception(f"Undefined variable: {name}")

    elif isinstance(node, BinaryOpNode):
        op = node.operator
        # Assignment as expression: x = expr
        if op == '=':
            if not isinstance(node.left, IdentifierNode):
                raise Exception('Left side of assignment must be a variable')
            value = evaluate(node.right, scope)
            scope[node.left.name] = value
            return value
        left = evaluate(node.left, scope)
        right = evaluate(node.right, scope)
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
        # Otomatik tip dönüşümü: int x = input(); gibi durumlar için
        if hasattr(node, 'var_type'):
            if node.var_type == 'int' and isinstance(value, str):
                try:
                    value = int(value)
                except Exception:
                    raise Exception(f"Cannot convert input to int: {value}")
            elif node.var_type == 'float' and isinstance(value, str):
                try:
                    value = float(value)
                except Exception:
                    raise Exception(f"Cannot convert input to float: {value}")
        scope[node.name] = value

    elif isinstance(node, PrintNode):
        value = evaluate(node.value, scope)
        
        if value is None:
            print('null')
        else:
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
    
    elif isinstance(node, ForNode):
        # For döngüsünde ana scope'u kullan, böylece x gibi dış değişkenler güncellenir
        evaluate(node.init, scope)
        while evaluate(node.condition, scope):
            evaluate(node.body, scope)
            evaluate(node.increment, scope)
    
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