import argparse
import cmd
import shlex
from typing import Callable, Literal, NewType, Optional, TypeGuard


def trap[T](fn: Callable[[], T]) -> tuple[T, Literal[None]] | tuple[Literal[None], Exception]:
    try:
        return fn(), None
    except Exception as e:
        return None, e


TUserName = NewType('TUserName', str)
TTaskName = NewType('TTaskName', str)
TListName = NewType('TListName', str)


class TTask:
    def __init__(self, task_name: TTaskName) -> None:
        self.task_name = task_name
        self.status = False

    def disp(self) -> str:
        return f'{"[x]" if self.status else "[ ]"} {self.task_name}'


class TList:
    def __init__(
        self,
        owner: TUserName,
        list_name: TListName,
        tasks: list[TTask]
    ) -> None:
        self.owner = owner
        self.list_name = list_name
        self.tasks = tasks
        self.readers: list[TUserName] = []
        self.editors: list[TUserName] = []

    def disp(self) -> str:
        return f'{self.owner}/{self.list_name}'


class InvalidArgumentError(Exception):
    pass


class TinyTodoShell(cmd.Cmd):
    intro = 'Welcome to the tinytodo shell. Type help or ? to list commands.\n'
    prompt = 'tinytodo(guest)> '

    __login: Optional[TUserName] = TUserName('guest')
    __lists: list[TList] = []

    def _assert_args_len(self, expected_len: int, args: list[str], help: str) -> None:
        if len(args) != expected_len:
            raise InvalidArgumentError(help)

    def _assert_login(self, arg: Optional[TUserName]) -> TypeGuard[TUserName]:
        if self.__login is None:
            raise RuntimeError('Not logged in')

        return True

    def _get_list(self, owner: TUserName, list_name: TListName) -> tuple[int, TList]:
        for i, list_ in enumerate(self.__lists):
            if list_.owner == owner and list_.list_name == list_name:
                return i, list_

        raise RuntimeError('List not found')

    def _get_task(self, owner: TUserName, list_name: TListName, task_name: TTaskName) -> tuple[TList, int, TTask]:
        _, list_ = self._get_list(owner, list_name)

        for i, task in enumerate(list_.tasks):
            if task.task_name == task_name:
                return list_, i, task

        raise RuntimeError('Task not found')

    def _parse_list_name(self, list_name: str) -> tuple[TUserName, TListName]:
        if '/' in list_name:
            owner, list_name = list_name.split('/', 1)

            if '/' in list_name:
                raise RuntimeError('Invalid list name: Use of "/" in list name is not allowed')

            owner = TUserName(owner)
            list_name = TListName(list_name)

        else:
            assert self._assert_login(self.__login)
            owner = self.__login
            list_name = TListName(list_name)

        return owner, list_name

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
        assert self._assert_login(self.__login)

        list_name = TListName(args[0])

        if '/' in list_name:
            raise RuntimeError('Invalid list name: Use of "/" in list name is not allowed')

        if any((self.__login, list_name) == elm for elm in [(elm.owner, elm.list_name) for elm in self.__lists]):
            raise RuntimeError('List already exists')

        self.__lists.append(TList(self.__login, list_name, []))

    def do_list_lists(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'list_lists')
        assert self._assert_login(self.__login)

        for list_ in self.__lists:
            if not list_.owner == self.__login:
                continue

            print(list_.disp())

    def do_delete_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'delete_list [<owner_name>/]<list_name>')

        owner, list_name = self._parse_list_name(args[0])

        i, _ = self._get_list(owner, list_name)
        del self.__lists[i]

    def do_put_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'put_task [<owner_name>/]<list_name> <task_name>')

        owner, list_name = self._parse_list_name(args[0])
        task_name = TTaskName(args[1])

        task, _ = trap(lambda: self._get_task(owner, list_name, task_name))

        if task is not None:
            raise RuntimeError('Task already exists')

        _, list_ = self._get_list(owner, list_name)
        list_.tasks.append(TTask(task_name))

    def do_list_tasks(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'list_tasks [<owner_name>/]<list_name>')

        owner, list_name = self._parse_list_name(args[0])

        _, list_ = self._get_list(owner, list_name)
        for task in list_.tasks:
            print(task.disp())

    def do_toggle_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'toggle_task [<owner_name>/]<list_name> <task_name>')

        owner, list_name = self._parse_list_name(args[0])
        task_name = TTaskName(args[1])

        _, _, task = self._get_task(owner, list_name, task_name)

        task.status = not task.status

    def do_delete_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'delete_task [<owner_name>/]<list_name> <task_name>')

        owner, list_name = self._parse_list_name(args[0])
        task_name = TTaskName(args[1])

        list_, i, _ = self._get_task(owner, list_name, task_name)
        del list_.tasks[i]

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
