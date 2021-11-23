from argparse import ArgumentParser
from pathlib import Path
from pylox.environment import Environment

from pylox.parser import parse
from pylox.interpreter import interpret
from pylox.scanner import scan_tokens


def run(input: str, env: Environment = None) -> None:
    env = env or Environment()
    tokens = scan_tokens(input)
    program = parse(tokens)
    interpret(program, env)


def run_file(input_path: Path) -> None:
    with open(input_path) as file:
        input_text = file.read()
        run(input_text)


def run_prompt() -> None:
    env = Environment()
    try:
        while True:
            print("> ", end="")
            line = input()
            if line:
                run(line, env)
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
