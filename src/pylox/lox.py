from argparse import ArgumentParser
from pathlib import Path

from pylox.parser import parse
from pylox.interpreter import interpret
from pylox.scanner import scan_tokens


def run(input: str) -> None:
    tokens = scan_tokens(input)
    expr = parse(tokens)
    print(interpret(expr))


def run_file(input_path: Path) -> None:
    with open(input_path) as file:
        input_text = file.read()
        run(input_text)


def run_prompt() -> None:
    try:
        while True:
            print("> ", end="")
            line = input()
            if line:
                run(line)
    except KeyboardInterrupt:
        print("--=Exiting pylox.=--")


if __name__ == "__main__":
    parser = ArgumentParser(description="pylox lox interpreter")
    parser.add_argument("path", help="file to interpret", nargs="?")
    args = parser.parse_args()

    if args.path:
        run_file(Path(args.path))
    else:
        run_prompt()
