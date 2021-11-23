from pylox.expr import Binary, Expr, Grouping, Literal, Unary


def _is_truthy(val: object):
    return val not in [False, None]


def interpret(expr: Expr) -> object:
    match expr:
        case Literal(value):
            return value
        case Binary(left, operator, right):
            lhs = interpret(left)
            rhs = interpret(right)
            match operator.lexeme:
                case "+":
                    return lhs + rhs
                case "-":
                    return lhs - rhs
                case "*":
                    return lhs * rhs
                case "/":
                    return lhs / rhs
        case Unary(operator, right):
            rhs = interpret(right)
            match operator.lexeme:
                case "!":
                    return not _is_truthy(rhs)
                case "-":
                    return -rhs
        case Grouping(expr):
            return interpret(expr)
