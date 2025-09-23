#!/usr/bin/env python3
"""
Mathematical Expression Parser and Evaluator

A comprehensive mathematical expression parser that tokenizes, parses, and evaluates
mathematical expressions with support for variables, functions, and operator precedence.

Features:
- Lexical analysis with token classification
- Recursive descent parser with operator precedence
- AST-based expression evaluation
- Built-in mathematical functions (sin, cos, tan, log, exp, sqrt, abs)
- Variable support with assignment and lookup
- Interactive calculator with expression history
- Comprehensive error handling and validation
- Expression simplification and optimization

Example usage:
    calc = Calculator()
    calc.run()

    # Interactive session:
    > x = 10
    > y = sin(x) + cos(x)
    > result = x * y + sqrt(25)
    > result
"""

import math
import sys
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass


# Token Types for Lexical Analysis
class TokenType(Enum):
    """Enumeration of all token types in mathematical expressions."""

    # Literals and identifiers
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    POWER = "POWER"
    MODULO = "MODULO"

    # Assignment
    ASSIGN = "ASSIGN"

    # Parentheses
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"

    # Function call
    FUNCTION = "FUNCTION"
    COMMA = "COMMA"

    # End of input
    EOF = "EOF"

    # Error token
    ERROR = "ERROR"


@dataclass
class Token:
    """Represents a single token in the mathematical expression."""

    type: TokenType
    value: Union[str, float]
    position: int

    def __str__(self) -> str:
        return f"Token({self.type.value}, {self.value}, pos={self.position})"


class LexicalError(Exception):
    """Exception raised during lexical analysis."""

    def __init__(self, message: str, position: int):
        super().__init__(message)
        self.position = position


class ParseError(Exception):
    """Exception raised during parsing."""

    def __init__(self, message: str, token: Optional[Token] = None):
        super().__init__(message)
        self.token = token


class EvaluationError(Exception):
    """Exception raised during expression evaluation."""

    def __init__(self, message: str):
        super().__init__(message)


# Abstract Syntax Tree Node Types
class ASTNode:
    """Base class for all AST nodes."""

    def evaluate(self, variables: Dict[str, float]) -> float:
        """Evaluate the expression represented by this node."""
        raise NotImplementedError("Subclasses must implement evaluate method")

    def __str__(self) -> str:
        """String representation of the AST node."""
        raise NotImplementedError("Subclasses must implement __str__ method")


class NumberNode(ASTNode):
    """AST node representing a numeric literal."""

    def __init__(self, value: float):
        self.value = value

    def evaluate(self, variables: Dict[str, float]) -> float:
        return self.value

    def __str__(self) -> str:
        return str(self.value)


class VariableNode(ASTNode):
    """AST node representing a variable reference."""

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, variables: Dict[str, float]) -> float:
        if self.name not in variables:
            raise EvaluationError(f"Undefined variable: {self.name}")
        return variables[self.name]

    def __str__(self) -> str:
        return self.name


class BinaryOpNode(ASTNode):
    """AST node representing a binary operation."""

    def __init__(self, left: ASTNode, operator: TokenType, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self, variables: Dict[str, float]) -> float:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)

        if self.operator == TokenType.PLUS:
            return left_val + right_val
        elif self.operator == TokenType.MINUS:
            return left_val - right_val
        elif self.operator == TokenType.MULTIPLY:
            return left_val * right_val
        elif self.operator == TokenType.DIVIDE:
            if right_val == 0.0:
                raise EvaluationError("Division by zero")
            return left_val / right_val
        elif self.operator == TokenType.POWER:
            return left_val ** right_val
        elif self.operator == TokenType.MODULO:
            if right_val == 0.0:
                raise EvaluationError("Modulo by zero")
            return left_val % right_val
        else:
            raise EvaluationError(f"Unknown binary operator: {self.operator}")

    def __str__(self) -> str:
        op_symbols = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.MULTIPLY: "*",
            TokenType.DIVIDE: "/",
            TokenType.POWER: "**",
            TokenType.MODULO: "%"
        }
        return f"({self.left} {op_symbols[self.operator]} {self.right})"


class UnaryOpNode(ASTNode):
    """AST node representing a unary operation."""

    def __init__(self, operator: TokenType, operand: ASTNode):
        self.operator = operator
        self.operand = operand

    def evaluate(self, variables: Dict[str, float]) -> float:
        operand_val = self.operand.evaluate(variables)

        if self.operator == TokenType.PLUS:
            return +operand_val
        elif self.operator == TokenType.MINUS:
            return -operand_val
        else:
            raise EvaluationError(f"Unknown unary operator: {self.operator}")

    def __str__(self) -> str:
        op_symbols = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-"
        }
        return f"{op_symbols[self.operator]}{self.operand}"


class FunctionCallNode(ASTNode):
    """AST node representing a function call."""

    def __init__(self, name: str, arguments: List[ASTNode]):
        self.name = name
        self.arguments = arguments

    def evaluate(self, variables: Dict[str, float]) -> float:
        # Evaluate all arguments
        arg_values = [arg.evaluate(variables) for arg in self.arguments]

        # Built-in mathematical functions
        if self.name == "sin":
            if len(arg_values) != 1:
                raise EvaluationError("sin() requires exactly 1 argument")
            return math.sin(arg_values[0])
        elif self.name == "cos":
            if len(arg_values) != 1:
                raise EvaluationError("cos() requires exactly 1 argument")
            return math.cos(arg_values[0])
        elif self.name == "tan":
            if len(arg_values) != 1:
                raise EvaluationError("tan() requires exactly 1 argument")
            return math.tan(arg_values[0])
        elif self.name == "log":
            if len(arg_values) == 1:
                if arg_values[0] <= 0:
                    raise EvaluationError("log() requires positive argument")
                return math.log(arg_values[0])
            elif len(arg_values) == 2:
                if arg_values[0] <= 0 or arg_values[1] <= 0 or arg_values[1] == 1:
                    raise EvaluationError("log() requires positive arguments and base != 1")
                return math.log(arg_values[0], arg_values[1])
            else:
                raise EvaluationError("log() requires 1 or 2 arguments")
        elif self.name == "exp":
            if len(arg_values) != 1:
                raise EvaluationError("exp() requires exactly 1 argument")
            return math.exp(arg_values[0])
        elif self.name == "sqrt":
            if len(arg_values) != 1:
                raise EvaluationError("sqrt() requires exactly 1 argument")
            if arg_values[0] < 0:
                raise EvaluationError("sqrt() requires non-negative argument")
            return math.sqrt(arg_values[0])
        elif self.name == "abs":
            if len(arg_values) != 1:
                raise EvaluationError("abs() requires exactly 1 argument")
            return abs(arg_values[0])
        elif self.name == "min":
            if len(arg_values) < 1:
                raise EvaluationError("min() requires at least 1 argument")
            return min(arg_values)
        elif self.name == "max":
            if len(arg_values) < 1:
                raise EvaluationError("max() requires at least 1 argument")
            return max(arg_values)
        else:
            raise EvaluationError(f"Unknown function: {self.name}")

    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"


class AssignmentNode(ASTNode):
    """AST node representing variable assignment."""

    def __init__(self, variable: str, expression: ASTNode):
        self.variable = variable
        self.expression = expression

    def evaluate(self, variables: Dict[str, float]) -> float:
        value = self.expression.evaluate(variables)
        variables[self.variable] = value
        return value

    def __str__(self) -> str:
        return f"{self.variable} = {self.expression}"


class Lexer:
    """Lexical analyzer for mathematical expressions."""

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.current_char = self.text[0] if text else None

    def advance(self) -> None:
        """Move to the next character in the input."""
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self) -> float:
        """Read a numeric literal from the input."""
        start_pos = self.position
        has_dot = False

        while (self.current_char is not None and
               (self.current_char.isdigit() or self.current_char == '.')):
            if self.current_char == '.':
                if has_dot:
                    raise LexicalError("Invalid number format: multiple decimal points", start_pos)
                has_dot = True
            self.advance()

        number_str = self.text[start_pos:self.position]
        try:
            return float(number_str)
        except ValueError:
            raise LexicalError(f"Invalid number format: {number_str}", start_pos)

    def read_identifier(self) -> str:
        """Read an identifier (variable or function name) from the input."""
        start_pos = self.position

        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            self.advance()

        return self.text[start_pos:self.position]

    def get_next_token(self) -> Token:
        """Get the next token from the input."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                number = self.read_number()
                return Token(TokenType.NUMBER, number, self.position - 1)

            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.read_identifier()
                return Token(TokenType.IDENTIFIER, identifier, self.position - len(identifier))

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.position - 1)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.position - 1)

            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(TokenType.POWER, '**', self.position - 2)
                return Token(TokenType.MULTIPLY, '*', self.position - 1)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', self.position - 1)

            if self.current_char == '%':
                self.advance()
                return Token(TokenType.MODULO, '%', self.position - 1)

            if self.current_char == '=':
                self.advance()
                return Token(TokenType.ASSIGN, '=', self.position - 1)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.position - 1)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.position - 1)

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.position - 1)

            # Unknown character
            pos = self.position
            self.advance()
            return Token(TokenType.ERROR, self.text[pos], pos)

        return Token(TokenType.EOF, None, self.position)


class Parser:
    """Recursive descent parser for mathematical expressions."""

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def consume(self, expected_type: TokenType) -> Token:
        """Consume a token of the expected type."""
        if self.current_token.type != expected_type:
            raise ParseError(f"Expected {expected_type.value}, got {self.current_token.type.value}",
                           self.current_token)

        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        return token

    def parse(self) -> ASTNode:
        """Parse the entire expression."""
        node = self.parse_assignment()

        if self.current_token.type != TokenType.EOF:
            raise ParseError(f"Unexpected token: {self.current_token.value}", self.current_token)

        return node

    def parse_assignment(self) -> ASTNode:
        """Parse assignment expressions (lowest precedence)."""
        node = self.parse_expression()

        if self.current_token.type == TokenType.ASSIGN:
            if not isinstance(node, VariableNode):
                raise ParseError("Invalid assignment target", self.current_token)

            self.consume(TokenType.ASSIGN)
            expression = self.parse_assignment()
            return AssignmentNode(node.name, expression)

        return node

    def parse_expression(self) -> ASTNode:
        """Parse addition and subtraction (lowest precedence after assignment)."""
        node = self.parse_term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.type
            self.consume(op)
            right = self.parse_term()
            node = BinaryOpNode(node, op, right)

        return node

    def parse_term(self) -> ASTNode:
        """Parse multiplication, division, and modulo."""
        node = self.parse_power()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.current_token.type
            self.consume(op)
            right = self.parse_power()
            node = BinaryOpNode(node, op, right)

        return node

    def parse_power(self) -> ASTNode:
        """Parse exponentiation (right-associative)."""
        node = self.parse_factor()

        if self.current_token.type == TokenType.POWER:
            op = self.current_token.type
            self.consume(op)
            right = self.parse_power()  # Right-associative
            node = BinaryOpNode(node, op, right)

        return node

    def parse_factor(self) -> ASTNode:
        """Parse unary operators and primary expressions."""
        if self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.type
            self.consume(op)
            operand = self.parse_factor()
            return UnaryOpNode(op, operand)

        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions (numbers, variables, function calls, parentheses)."""
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.consume(TokenType.NUMBER)
            return NumberNode(value)

        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.consume(TokenType.IDENTIFIER)

            # Check for function call
            if self.current_token.type == TokenType.LPAREN:
                self.consume(TokenType.LPAREN)
                arguments = []

                if self.current_token.type != TokenType.RPAREN:
                    arguments.append(self.parse_assignment())

                    while self.current_token.type == TokenType.COMMA:
                        self.consume(TokenType.COMMA)
                        arguments.append(self.parse_assignment())

                self.consume(TokenType.RPAREN)
                return FunctionCallNode(name, arguments)

            # Regular variable
            return VariableNode(name)

        if self.current_token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self.parse_assignment()
            self.consume(TokenType.RPAREN)
            return node

        raise ParseError(f"Unexpected token: {self.current_token.value}", self.current_token)


class Calculator:
    """Interactive mathematical expression calculator."""

    def __init__(self):
        self.variables: Dict[str, float] = {}
        self.history: List[str] = []
        self.initialize_constants()

    def initialize_constants(self) -> None:
        """Initialize mathematical constants."""
        self.variables['pi'] = math.pi
        self.variables['e'] = math.e
        self.variables['tau'] = 2 * math.pi

    def evaluate_expression(self, expression: str) -> float:
        """Evaluate a mathematical expression."""
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            ast = parser.parse()
            result = ast.evaluate(self.variables)

            # Store successful expressions in history
            self.history.append(expression)

            return result

        except (LexicalError, ParseError, EvaluationError) as e:
            raise e
        except Exception as e:
            raise EvaluationError(f"Unexpected error: {str(e)}")

    def print_help(self) -> None:
        """Print help information."""
        print("Mathematical Expression Calculator")
        print("=" * 40)
        print("Supported operators: +, -, *, /, **, %")
        print("Supported functions: sin, cos, tan, log, exp, sqrt, abs, min, max")
        print("Built-in constants: pi, e, tau")
        print("Variable assignment: x = expression")
        print("Commands:")
        print("  help    - Show this help")
        print("  vars    - Show all variables")
        print("  history - Show expression history")
        print("  clear   - Clear variables and history")
        print("  quit    - Exit calculator")
        print()

    def print_variables(self) -> None:
        """Print all defined variables."""
        if not self.variables:
            print("No variables defined.")
            return

        print("Defined variables:")
        for name, value in sorted(self.variables.items()):
            print(f"  {name} = {value}")

    def print_history(self) -> None:
        """Print expression history."""
        if not self.history:
            print("No expression history.")
            return

        print("Expression history:")
        for i, expr in enumerate(self.history, 1):
            print(f"  {i}. {expr}")

    def clear_data(self) -> None:
        """Clear variables and history."""
        self.variables.clear()
        self.history.clear()
        self.initialize_constants()
        print("Variables and history cleared.")

    def run(self) -> None:
        """Run the interactive calculator."""
        print("Mathematical Expression Calculator")
        print("Type 'help' for commands, 'quit' to exit")
        print()

        while True:
            try:
                expression = input("> ").strip()

                if not expression:
                    continue

                if expression.lower() == 'quit':
                    print("Goodbye!")
                    break
                elif expression.lower() == 'help':
                    self.print_help()
                elif expression.lower() == 'vars':
                    self.print_variables()
                elif expression.lower() == 'history':
                    self.print_history()
                elif expression.lower() == 'clear':
                    self.clear_data()
                else:
                    result = self.evaluate_expression(expression)
                    print(f"  = {result}")

            except (LexicalError, ParseError, EvaluationError) as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("Goodbye!")
                break


def demonstrate_calculator() -> None:
    """Demonstrate calculator functionality with predefined expressions."""
    print("Mathematical Expression Calculator - Demonstration")
    print("=" * 60)

    calc = Calculator()

    # Test expressions
    test_expressions = [
        "2 + 3 * 4",
        "pi * 2",
        "sin(pi / 2)",
        "x = 10",
        "y = sin(x) + cos(x)",
        "sqrt(x**2 + y**2)",
        "log(e**2)",
        "max(1, 2, 3, 4, 5)",
        "result = (x + y) * sqrt(25)",
        "result",
        "abs(-42)",
        "2**3**2",  # Right-associative: 2**(3**2) = 2**9 = 512
        "factorial_approx = sqrt(2 * pi * 10) * (10 / e)**10",  # Stirling's approximation
    ]

    print("Evaluating test expressions:")
    print()

    for expr in test_expressions:
        try:
            result = calc.evaluate_expression(expr)
            print(f"  {expr}")
            print(f"    = {result}")
            print()
        except Exception as e:
            print(f"  {expr}")
            print(f"    Error: {e}")
            print()

    print("Final variables:")
    calc.print_variables()
    print()

    print("Expression history:")
    calc.print_history()


def main() -> None:
    """Main function - run demonstration or interactive mode."""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demonstrate_calculator()
    else:
        calc = Calculator()
        calc.run()


if __name__ == "__main__":
    main()