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

        if any((self.__login, list_name) == elm for elm in [(elm.owner, elm.list_name) for elm in self.__lists]):
            raise RuntimeError('List already exists')

        self.__lists.append(TList(self.__login, list_name, []))

    def do_list_lists(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(0, args, 'list_lists')
        assert self._assert_login(self.__login)

        for list_ in self.__lists:
            if not (
                list_.owner == self.__login or
                self.__login in list_.readers or
                self.__login in list_.editors
            ):
                continue

            print(list_.list_name)

    def do_delete_list(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'delete_list <list_name>')
        assert self._assert_login(self.__login)

        list_name = TListName(args[0])

        i, _ = self._get_list(self.__login, list_name)
        del self.__lists[i]

    def do_put_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'put_task <list_name> <task_name>')
        assert self._assert_login(self.__login)

        owner = self.__login
        list_name = TListName(args[0])
        task_name = TTaskName(args[1])

        task, _ = trap(lambda: self._get_task(owner, list_name, task_name))

        if task is not None:
            raise RuntimeError('Task already exists')

        _, list_ = self._get_list(owner, list_name)
        list_.tasks.append(TTask(task_name))


    def do_list_tasks(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(1, args, 'list_tasks <list_name>')
        assert self._assert_login(self.__login)

        list_name = TListName(args[0])

        _, list_ = self._get_list(self.__login, list_name)
        for task in list_.tasks:
            print(f'{"[x]" if task.status else "[ ]"} {task.task_name}')

    def do_toggle_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'toggle_task <list_name> <task_name>')
        assert self._assert_login(self.__login)

        list_name = TListName(args[0])
        task_name = TTaskName(args[1])

        _, _, task = self._get_task(self.__login, list_name, task_name)

        task.status = not task.status

    def do_delete_task(self, line: str) -> None:
        args = shlex.split(line)
        self._assert_args_len(2, args, 'delete_task <list_name> <task_name>')
        assert self._assert_login(self.__login)

        list_name = TListName(args[0])
        task_name = TTaskName(args[1])

        list_, i, _ = self._get_task(self.__login, list_name, task_name)
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
