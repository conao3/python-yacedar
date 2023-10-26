import argparse
import cmd
from typing import NewType, Optional


TUserName = NewType('TUserName', str)
TListName = NewType('TListName', str)
TTaskName = NewType('TTaskName', str)
TTask = NewType('TTask', str)
TList = NewType('TList', dict[TTaskName, list[TTask]])

class TinyTodoShell(cmd.Cmd):
    intro = 'Welcome to the tinytodo shell. Type help or ? to list commands.\n'
    prompt = 'tinytodo> '

    __login: Optional[TUserName] = TUserName('guest')
    __lists: dict[TUserName, TList] = {}

    def do_login(self, line: str) -> None:
        self.__login = TUserName(line)

    def do_logout(self, line: str) -> None:
        self.__login = None

    def do_list_lists(self, line: str) -> None:
        self.columnize(list(self.__lists.keys()))

    def do_put_list(self, line: str) -> None:
        if line in self.__lists:
            print('List already exists')
        else:
            self.__lists[TUserName(line)] = TList({})

    def postcmd(self, stop: bool, line: str) -> bool:
        self.prompt = 'tinytodo' + (f'({self.__login})' if self.__login else '') + '> '
        return super().postcmd(stop, line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        TinyTodoShell().cmdloop()
    except KeyboardInterrupt:
        print('')
