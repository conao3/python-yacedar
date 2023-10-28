import argparse
import cmd
import shlex
from typing import Callable, Literal, NewType


def trap[T](fn: Callable[[], T]) -> tuple[T, Literal[None]] | tuple[Literal[None], Exception]:
    try:
        return fn(), None
    except Exception as e:
        return None, e


TUserName = NewType('TUserName', str)
TTaskNo = NewType('TTaskNo', int)
TListNo = NewType('TListNo', int)


class TTask:
    def __init__(self, task_no: TTaskNo, task_name: str) -> None:
        self.task_no = task_no
        self.task_name = task_name
        self.status = False

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
        tasks: dict[TTaskNo, TTask] = {}
    ) -> None:
        self.owner = owner
        self.list_no = list_no
        self.list_name = list_name
        self.tasks = tasks
        self.readers: list[TUserName] = []
        self.editors: list[TUserName] = []

        self.counter_task_no = 0

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
    def __init__(self) -> None:
        self.name: TUserName
        self.lists: dict[TListNo, TList] = {}

        self.counter_list_no = 0

    def new_list_no(self) -> TListNo:
        ret = TListNo(self.counter_list_no)
        self.counter_list_no += 1
        return ret


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
            self.__lists[self.__login] = TUser()

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

    try:
        TinyTodoShell().cmdloop()
    except KeyboardInterrupt:
        print('')
