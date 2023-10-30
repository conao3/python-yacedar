import argparse
import cmd
import pathlib
import shlex
from typing import Any, Callable, Literal, NewType
import typing

import yaml


def trap[T](fn: Callable[[], T]) -> tuple[T, Literal[None]] | tuple[Literal[None], Exception]:
    try:
        return fn(), None
    except Exception as e:
        return None, e


TUserName = NewType('TUserName', str)
TTaskNo = NewType('TTaskNo', int)
TListNo = NewType('TListNo', int)


class TTask:
    def __init__(
        self,
        task_no: TTaskNo,
        task_name: str,
        status: bool = False
    ) -> None:
        self.task_no = task_no
        self.task_name = task_name
        self.status = status

    def disp_oneline(self) -> str:
        return f'{self.task_no}) {"[x]" if self.status else "[ ]"} {self.task_name}'

    def disp(self) -> str:
        return f'{"[x]" if self.status else "[ ]"} {self.task_name}'


class TList:
    def __init__(
        self,
        owner: TUserName,
        list_no: int,
        list_name: str,
        tasks: dict[TTaskNo, TTask] = {},
        readers: list[TUserName] = [],
        editors: list[TUserName] = [],
        counter_task_no: int = 0,
    ) -> None:
        self.owner = owner
        self.list_no = list_no
        self.list_name = list_name
        self.tasks = tasks
        self.readers = readers
        self.editors = editors

        self.counter_task_no = counter_task_no

    def new_task_no(self) -> TTaskNo:
        ret = TTaskNo(self.counter_task_no)
        self.counter_task_no += 1
        return ret

    def disp_oneline(self) -> str:
        return f'{self.owner}/{self.list_no}: {self.list_name}'

    def disp(self) -> str:
        return f'''\
Owner: {self.owner}
List No: {self.list_no}
List Name: {self.list_name}
Tasks:
{"\n".join(f"  {task.disp_oneline()}" for task in self.tasks.values())}'''


class TUser:
    def __init__(
        self,
        name: TUserName,
        lists: dict[TListNo, TList] = {},
        counter_list_no: int = 0,
    ) -> None:
        self.name = name
        self.lists = lists

        self.counter_list_no = counter_list_no

    def new_list_no(self) -> TListNo:
        ret = TListNo(self.counter_list_no)
        self.counter_list_no += 1
        return ret


def new_database(dct: dict[str, Any]) -> dict[TUserName, TUser]:
    def new_task(dct: dict[str, Any]) -> TTask:
        return TTask(
            TTaskNo(dct['task_no']),
            dct['task_name'],
            dct['status'],
        )

    def new_list(dct: dict[str, Any]) -> TList:
        tasks = {no: new_task(task_dct) for no, task_dct in dct['tasks'].items()}
        return TList(
            owner=TUserName(dct['owner']),
            list_no=TListNo(dct['list_no']),
            list_name=dct['list_name'],
            tasks=tasks,
            readers=typing.cast(list[TUserName], dct.get('readers', [])),
            editors=typing.cast(list[TUserName], dct.get('editors', [])),
            counter_task_no=max(task.task_no for task in tasks.values()),
        )

    def new_user(dct: dict[str, Any]) -> TUser:
        lists = {no: new_list(list_dct) for no, list_dct in dct['lists'].items()}
        return TUser(
            name=TUserName(dct['name']),
            lists=lists,
            counter_list_no=max(list_.list_no for list_ in lists.values()),
        )

    return {TUserName(name): new_user(user_dct) for name, user_dct in dct.items()}


class InvalidArgumentError(Exception):
    pass


class TinyTodoShell(cmd.Cmd):
    intro = 'Welcome to the tinytodo shell. Type help or ? to list commands.\n'
    prompt = 'tinytodo(guest)> '

    __login: TUserName = TUserName('guest')
    __lists: dict[TUserName, TUser] = {}

    def _assert_args_len(self, expected_len: int, args: list[str], help: str) -> None:
        if len(args) != expected_len:
            raise InvalidArgumentError(help)

    def _parse_list_name(self, arg: str) -> tuple[TUserName, TListNo]:
        if '/' in arg:
            owner_, list_no_ = arg.split('/', 1)

            owner = TUserName(owner_)
            arg = list_no_

        else:
            owner = self.__login

        return owner, TListNo(int(arg))

    def do_login(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'login <user_name>')

        self.__login = TUserName(args[0])

        if self.__login not in self.__lists:
            self.__lists[self.__login] = TUser(name=self.__login)

        print(f'Logged in as {self.__login}')

    def do_logout(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'logout')

        self.__login = TUserName('guest')

        print(f'Logged out.  Now you are {self.__login}')

    def do_put_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'put_list <list_name>')

        user = self.__lists[self.__login]
        list_no = user.new_list_no()

        user.lists[list_no] = TList(self.__login, list_no, args[0])

        print(f'List {list_no} created.')

    def do_get_lists(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'get_lists')

        for list_ in self.__lists[self.__login].lists.values():
            print(list_.disp_oneline())

    def do_get_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'get_list [<owner_name>/]<list_no>')

        list_no = TListNo(int(args[0]))

        print(self.__lists[self.__login].lists[list_no].disp())

    def do_delete_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'delete_list <list_no>')

        list_no = TListNo(int(args[0]))

        del self.__lists[self.__login].lists[list_no]

        print(f'List {list_no} deleted.')

    def do_put_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'put_task <list_no> <task_name>')

        list_no = TListNo(int(args[0]))

        user = self.__lists[self.__login]
        list_ = user.lists[list_no]
        task_no = list_.new_task_no()

        list_.tasks[task_no] = TTask(task_no, args[1])

        print(f'Task {task_no} created on List {list_no}.')

    def do_toggle_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'toggle_task [<owner_name>/]<list_no> <task_no>')

        list_no = TListNo(int(args[0]))
        task_no = TTaskNo(int(args[1]))

        task = self.__lists[self.__login].lists[list_no].tasks[task_no]
        task.status = not task.status

        print(f'Task {task_no} toggled on List {list_no}.')

    def do_delete_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'delete_task [<owner_name>/]<list_no> <task_no>')

        list_no = TListNo(int(args[0]))
        task_no = TTaskNo(int(args[1]))

        del self.__lists[self.__login].lists[list_no].tasks[task_no]

        print(f'Task {task_no} deleted on List {list_no}.')

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

    assets_path = pathlib.Path(__file__).parent / 'assets'
    initial_data_file = assets_path / 'initial_data.yml'

    initial_data = yaml.safe_load(initial_data_file.read_text())

    try:
        app = TinyTodoShell()
        app._TinyTodoShell__lists = new_database(initial_data)  # type: ignore
        app.cmdloop()
    except KeyboardInterrupt:
        print('')
