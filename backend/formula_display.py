class FormulaParser:
    def __init__(self, text: str):
        self.text = text.replace(" ", "")
        self.pos = 0

    def parse(self):
        result = self.parse_expr()
        if self.pos != len(self.text):
            raise ValueError(f"Unexpected text at position {self.pos}: {self.text[self.pos:]}")
        return result

    def parse_expr(self):
        if self.peek_alpha():
            name = self.parse_name()

            if self.peek() == "(":
                self.consume("(")
                args = self.parse_args()
                self.consume(")")
                return (name, args)

            return name

        raise ValueError(f"Expected expression at position {self.pos}")

    def parse_args(self):
        args = [self.parse_expr()]

        while self.peek() == ",":
            self.consume(",")
            args.append(self.parse_expr())

        return args

    def parse_name(self):
        start = self.pos

        while self.pos < len(self.text) and self.text[self.pos].isalpha():
            self.pos += 1

        return self.text[start:self.pos]

    def peek(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek_alpha(self):
        return self.peek() is not None and self.peek().isalpha()

    def consume(self, char):
        if self.peek() != char:
            raise ValueError(f"Expected '{char}' at position {self.pos}")
        self.pos += 1


def formula_to_display(formula: str) -> str:
    parsed = FormulaParser(formula).parse()
    return render(parsed)


def render(node) -> str:
    if isinstance(node, str):
        return node

    op, args = node

    if op == "not":
        if len(args) != 1:
            raise ValueError("not expects 1 argument")
        child = args[0]
        if isinstance(child, str):
            return f"¬{render(child)}"
        return f"¬({render(child)})"

    if op == "and":
        check_binary(op, args)
        return f"({render(args[0])} ∧ {render(args[1])})"

    if op == "or":
        check_binary(op, args)
        return f"({render(args[0])} ∨ {render(args[1])})"

    if op == "imp":
        check_binary(op, args)
        return f"({render(args[0])} ⇒ {render(args[1])})"

    if op == "iff":
        check_binary(op, args)
        return f"({render(args[0])} ⇔ {render(args[1])})"

    raise ValueError(f"Unknown operator: {op}")


def check_binary(op: str, args: list):
    if len(args) != 2:
        raise ValueError(f"{op} expects 2 arguments")


if __name__ == "__main__":
    tests = [
        "or(p,not(p))",
        "iff(imp(p,q),or(not(p),q))",
        "iff(or(imp(not(r),and(not(p),not(q))),s),imp(or(p,q),or(r,s)))",
    ]

    for formula in tests:
        print(formula)
        print(formula_to_display(formula))
        print()