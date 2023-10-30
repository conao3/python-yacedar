from __future__ import annotations

import argparse
import cmd
import pathlib
import shlex
import textwrap
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


class TUser:
    def __init__(
        self,
        name: TUserName,
    ):
        self.name = name

    def disp(self, oneline: bool = False) -> str:
        return f'User Name: {self.name}'


class TList:
    def __init__(
        self,
        list_no: TListNo,
        list_name: str,
        owner: TUserName,
        reader: list[TUserName] = [],
        editer: list[TUserName] = [],
    ):
        self.list_no = list_no
        self.list_name = list_name
        self.owner = owner
        self.reader = reader
        self.editer = editer

    def disp(self, oneline: bool = False) -> str:
        if oneline:
            return f'{self.owner}/{self.list_no}: {self.list_name}'

        return f'''\
Owner: {self.owner}
List No: {self.list_no}
List Name: {self.list_name}'''


class TTask:
    def __init__(
        self,
        list_no: TListNo,
        task_no: TTaskNo,
        task_name: str,
        status: bool = False
    ):
        self.list_no = list_no
        self.task_no = task_no
        self.task_name = task_name
        self.status = status

    def disp(self, oneline: bool = False) -> str:
        return f'{"[x]" if self.status else "[ ]"} {self.task_name}'


class TDatabase:
    def __init__(
        self,
        users: dict[TUserName, TUser] = {},
        lists: dict[TListNo, TList] = {},
        tasks: dict[TListNo, dict[TTaskNo, TTask]] = {},
    ):
        self.users = users
        self.lists = lists
        self.tasks = tasks

    @classmethod
    def from_dict(cls, dct: dict[str, Any]) -> TDatabase:
        return cls(
            users={
                TUserName(name): TUser(name=name)
                for name in dct['users']
            },
            lists={
                TListNo(no): TList(
                    list_no=no,
                    list_name=val['list_name'],
                    owner=TUserName(val['owner'])
                )
                for no, val in dct['lists'].items()
            },
            tasks={
                TListNo(list_no): {
                    TTaskNo(task_no): TTask(
                        list_no=TListNo(list_no),
                        task_no=TTaskNo(task_no),
                        task_name=task['task_name'],
                        status=task['status']
                    )
                    for task_no, task in list_.items()
                }
                for list_no, list_ in dct['tasks'].items()
            },
        )

    def put_user(self, obj: TUser) -> None:
        self.users[obj.name] = obj

    def put_list(self, obj: TList) -> None:
        self.lists[obj.list_no] = obj

    def put_task(self, obj: TTask) -> None:
        if obj.list_no not in self.tasks:
            self.tasks[obj.list_no] = {}

        self.tasks[obj.list_no][obj.task_no] = obj

    def get_new_list_no(self) -> TListNo:
        return TListNo(max(self.lists.keys()) + 1)

    def get_new_task_no(self, list_no: TListNo) -> TTaskNo:
        return TTaskNo(max(self.tasks[list_no].keys()) + 1)

    def disp_user(self, obj: TUser) -> str:
        return obj.disp()

    def disp_list(self, obj: TList) -> str:
        tasks = '\n'.join([task.disp(oneline=True) for task in self.tasks[obj.list_no].values()])

        return f'''\
{obj.disp()}
Tasks:
{textwrap.indent(tasks, '  ')}'''

    def disp_task(self, obj: TTask) -> str:
        return obj.disp()


class InvalidArgumentError(Exception):
    pass


class TinyTodoShell(cmd.Cmd):
    intro = 'Welcome to the tinytodo shell. Type help or ? to list commands.\n'
    prompt = 'tinytodo(guest)> '

    __login: TUserName = TUserName('guest')
    __db: TDatabase = TDatabase()

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

        if self.__login not in self.__db.users:
            self.__db.users[self.__login] = TUser(name=self.__login)

        print(f'Logged in as {self.__login}')

    def do_logout(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'logout')

        self.__login = TUserName('guest')

        print(f'Logged out.  Now you are {self.__login}')

    def do_put_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'put_list <list_name>')

        list_no = self.__db.get_new_list_no()

        self.__db.put_list(TList(
            list_no=list_no,
            list_name=args[0],
            owner=self.__login,
        ))

        print(f'List {list_no} created.')

    def do_get_lists(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'get_lists')

        for list_ in self.__db.lists.values():
            print(list_.disp(oneline=True))

    def do_get_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'get_list [<owner_name>/]<list_no>')

        list_no = TListNo(int(args[0]))

        print(self.__db.disp_list(self.__db.lists[list_no]))

    def do_delete_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'delete_list <list_no>')

        list_no = TListNo(int(args[0]))

        del self.__db.lists[list_no]

        print(f'List {list_no} deleted.')

    def do_share_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(3, args, 'share_list <list_no> <user_name> <reader|editer>')

        list_no = TListNo(int(args[0]))
        user_name = TUserName(args[1])
        role = args[2]

        if role not in ['reader', 'editer']:
            raise InvalidArgumentError('share_list <list_no> <user_name> <reader|editer>')

        list_ = self.__db.lists[list_no]
        auth_users = getattr(list_, f'{role}s')
        if user_name in auth_users:
            raise InvalidArgumentError(f'{user_name} is already {role}.')

        auth_users.append(user_name)

    def do_put_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'put_task <list_no> <task_name>')

        list_no = TListNo(int(args[0]))
        task_name = args[1]

        task_no = self.__db.get_new_task_no(list_no)

        self.__db.put_task(TTask(
            list_no=list_no,
            task_no=task_no,
            task_name=task_name,
        ))

        print(f'Task {task_no} created on List {list_no}.')

    def do_toggle_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'toggle_task [<owner_name>/]<list_no> <task_no>')

        list_no = TListNo(int(args[0]))
        task_no = TTaskNo(int(args[1]))

        task = self.__db.tasks[list_no][task_no]
        task.status = not task.status

        print(f'Task {task_no} toggled on List {list_no}.')

    def do_delete_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'delete_task [<owner_name>/]<list_no> <task_no>')

        list_no = TListNo(int(args[0]))
        task_no = TTaskNo(int(args[1]))

        del self.__db.tasks[list_no][task_no]

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
        app._TinyTodoShell__db = TDatabase.from_dict(initial_data)  # type: ignore
        app.cmdloop()
    except KeyboardInterrupt:
        print('')
