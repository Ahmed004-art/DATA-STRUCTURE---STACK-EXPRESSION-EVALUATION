"""
DCOMP320 - Data Structures and Algorithms
Assignment: Stacks Implementation
Student : Ahmed Junior Kamara (ID: 905005337, Class: DIT201F)

Reads mathematical expressions from input.txt, evaluates each one using
stacks (shunting-yard style, with an operator stack and an operand stack),
and writes the results to output.txt using the same separator format.
"""

import os
import sys

INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

OPERATORS = {"+": 1, "-": 1, "*": 2, "/": 2}


class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


def tokenize(expression):
    """
    Convert an expression string into a list of tokens (numbers, operators,
    parentheses). A '-' or '+' is treated as a unary sign when it appears at
    the start of the expression, after '(' or after another operator; it is
    folded into the number that follows (e.g. -3, +2.5).
    """
    tokens = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
            continue

        previous = tokens[-1] if tokens else None
        expects_operand = previous is None or previous == "(" or previous in OPERATORS

        if ch.isdigit() or ch == "." or (ch in "+-" and expects_operand):
            start = i
            if ch in "+-":
                i += 1
                # Unary sign before a parenthesis: -(2+3) -> -1 * (2+3)
                j = i
                while j < n and expression[j].isspace():
                    j += 1
                if j < n and expression[j] == "(":
                    tokens.append(("-1" if ch == "-" else "1"))
                    tokens.append("*")
                    i = j
                    continue
            dot_count = 0
            digit_count = 0
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                if expression[i] == ".":
                    dot_count += 1
                else:
                    digit_count += 1
                i += 1
            text = expression[start:i]
            if digit_count == 0 or dot_count > 1:
                raise ValueError(f"invalid number '{text}'")
            tokens.append(text)
        elif ch in OPERATORS or ch in "()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"invalid character '{ch}'")
    return tokens


def apply_operator(operators, operands):
    """Pop one operator and two operands, compute, and push the result."""
    op = operators.pop()
    if operands.size() < 2:
        raise ValueError("malformed expression")
    right = operands.pop()
    left = operands.pop()
    if op == "+":
        operands.push(left + right)
    elif op == "-":
        operands.push(left - right)
    elif op == "*":
        operands.push(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        operands.push(left / right)


def evaluate_expression(expression):
    """
    Evaluate an arithmetic expression using two stacks:
      - operands stack : numbers
      - operators stack: operators and '('
    Supports +, -, *, /, parentheses and standard precedence.
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("empty expression")

    operands = Stack()
    operators = Stack()
    expect_operand = True  # used to detect malformed sequences

    for token in tokens:
        if token == "(":
            if not expect_operand:
                raise ValueError("malformed expression")
            operators.push(token)
        elif token == ")":
            if expect_operand:
                raise ValueError("malformed expression")
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators, operands)
            if operators.is_empty():
                raise ValueError("mismatched parentheses")
            operators.pop()  # discard '('
        elif token in OPERATORS:
            if expect_operand:
                raise ValueError("malformed expression")
            while (not operators.is_empty()
                   and operators.peek() != "("
                   and OPERATORS[operators.peek()] >= OPERATORS[token]):
                apply_operator(operators, operands)
            operators.push(token)
            expect_operand = True
        else:  # number
            if not expect_operand:
                raise ValueError("malformed expression")
            operands.push(float(token))
            expect_operand = False

    if expect_operand:
        raise ValueError("malformed expression")

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("mismatched parentheses")
        apply_operator(operators, operands)

    if operands.size() != 1:
        raise ValueError("malformed expression")
    return operands.pop()


def format_result(value):
    """Show whole numbers without a decimal point; round others to 4 d.p."""
    if value == int(value):
        return str(int(value))
    return str(round(value, 4))


def is_separator(line):
    """A separator line contains only dashes (e.g. -----)."""
    stripped = line.strip()
    return len(stripped) > 0 and set(stripped) == {"-"} and len(stripped) >= 3


def process_file(input_path=INPUT_FILE, output_path=OUTPUT_FILE):
    """
    Read expressions from input_path, evaluate each, and write the results to
    output_path, preserving the separator lines of the input.
    Returns the list of output lines.
    """
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.read().splitlines()

    output_lines = []
    for line in lines:
        if is_separator(line):
            output_lines.append(line.strip())      # keep the same separator
        elif line.strip() == "":
            continue                               # ignore blank lines
        else:
            try:
                output_lines.append(format_result(evaluate_expression(line)))
            except ZeroDivisionError:
                output_lines.append("Error: division by zero")
            except (ValueError, IndexError) as err:
                output_lines.append(f"Error: {err}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(output_lines) + "\n")
    return output_lines


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base, INPUT_FILE)
    output_path = os.path.join(base, OUTPUT_FILE)

    if not os.path.exists(input_path):
        print(f"Error: '{INPUT_FILE}' not found in {base}")
        sys.exit(1)

    print("Reading expressions from", INPUT_FILE)
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read().splitlines()

    results = process_file(input_path, output_path)

    print("\n{:<35} {}".format("EXPRESSION", "RESULT"))
    print("-" * 50)
    expressions = [l for l in source if l.strip() and not is_separator(l)]
    values = [r for r in results if not is_separator(r)]
    for expr, val in zip(expressions, values):
        print("{:<35} {}".format(expr.strip(), val))
    print("\nResults written to", OUTPUT_FILE)


if __name__ == "__main__":
    main()
