import argparse
import cmd
import shlex
from typing import NewType, Optional


TUserName = NewType('TUserName', str)
TTask = NewType('TTask', str)
TListName = NewType('TListName', str)
TList = NewType('TList', dict[TListName, dict[TTask, bool]])


class InvalidArgumentError(Exception):
    pass


class TinyTodoShell(cmd.Cmd):
    intro = 'Welcome to the tinytodo shell. Type help or ? to list commands.\n'
    prompt = 'tinytodo(guest)> '

    __login: Optional[TUserName] = TUserName('guest')
    __lists: dict[TUserName, TList] = {}

    def _assert_args_len(self, expected_len: int, args: list[str], help: str) -> None:
        if len(args) != expected_len:
            raise InvalidArgumentError(help)

    def do_login(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'login <user_name>')

        self.__login = TUserName(args[0])

    def do_logout(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'logout')

        self.__login = None

    def do_put_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'put_list <list_name>')

        list_name = TListName(args[0])

        if not self.__login:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (dct := self.__lists.get(self.__login)) is None:
            self.__lists[self.__login] = TList({list_name: {}})
        else:
            if list_name in dct:
                print('ERROR(RuntimeError): List already exists')
                return

            self.__lists[self.__login][list_name] = {}

    def do_list_lists(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'list_lists')

        if self.__login is None:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (lists := self.__lists.get(self.__login)) is None:
            print('ERROR(RuntimeError): No lists found')
            return

        self.columnize([str(elm) for elm in lists])

    def do_delete_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'delete_list <list_name>')

        list_name = TListName(args[0])

        if not self.__login:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (dct := self.__lists.get(self.__login)) is None:
            print('ERROR(RuntimeError): No lists found')
            return

        if list_name not in dct:
            print('ERROR(RuntimeError): List not found')
            return

        del dct[list_name]

    def do_put_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'put_task <list_name> <task_name>')

        list_name = TListName(args[0])
        task_name = TTask(args[1])

        if not self.__login:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (dct := self.__lists.get(self.__login)) is None:
            print('ERROR(RuntimeError): No lists found')
            return

        if (list_ := dct.get(list_name)) is None:
            print('ERROR(RuntimeError): List not found')
            return

        if task_name in list_:
            print('ERROR(RuntimeError): Task already exists')
            return

        list_[task_name] = False

    def do_list_tasks(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'list_tasks <list_name>')

        list_name = TListName(args[0])

        if not self.__login:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (dct := self.__lists.get(self.__login)) is None:
            print('ERROR(RuntimeError): No lists found')
            return

        if (list_ := dct.get(list_name)) is None:
            print('ERROR(RuntimeError): List not found')
            return

        for i, (task_name, status) in enumerate(list_.items()):
            print(f'{i+1}) {task_name}: {status}')

    def do_toggle_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'toggle_task <list_name> <task_name>')

        list_name = TListName(args[0])
        task_name = TTask(args[1])

        if not self.__login:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (dct := self.__lists.get(self.__login)) is None:
            print('ERROR(RuntimeError): No lists found')
            return

        if (list_ := dct.get(list_name)) is None:
            print('ERROR(RuntimeError): List not found')
            return

        if (status := list_.get(task_name)) is None:
            print('ERROR(RuntimeError): Task not found')
            return

        list_[task_name] = not status

    def do_delete_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'delete_task <list_name> <task_name>')

        list_name = TListName(args[0])
        task_name = TTask(args[1])

        if not self.__login:
            print('ERROR(RuntimeError): Not logged in')
            return

        if (dct := self.__lists.get(self.__login)) is None:
            print('ERROR(RuntimeError): No lists found')
            return

        if (list_ := dct.get(list_name)) is None:
            print('ERROR(RuntimeError): List not found')
            return

        if task_name not in list_:
            print('ERROR(RuntimeError): Task not found')
            return

        del list_[task_name]

    def onecmd(self, line: str) -> bool:
        try:
            return super().onecmd(line)
        except Exception as e:
            print(f'ERROR({type(e).__name__}): {e}')
            return False

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
