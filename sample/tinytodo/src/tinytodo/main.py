import argparse
import cmd


class TinyTodoShell(cmd.Cmd):
    intro = 'Welcome to the tinytodo shell. Type help or ? to list commands.\n'
    prompt = 'tinytodo> '


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    TinyTodoShell().cmdloop()
