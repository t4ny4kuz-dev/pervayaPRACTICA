"""Ядро эмулятора: разбор команд и их выполнение (без GUI)."""

from dataclasses import dataclass

from tokenizer import ParseError, parse_line

HOST_NAME = "emulator"
HOME_DIR = "~"


@dataclass
class Result:
    """Результат выполнения одной команды."""

    out: str = ""
    err: str = ""
    exit_requested: bool = False
    clear_requested: bool = False


class Shell:
    """Состояние и команды эмулируемой оболочки."""

    def __init__(self, vfs_name, user, host=HOST_NAME):
        """Создаёт оболочку для виртуальной ФС ``vfs_name``."""
        self.vfs_name = vfs_name
        self.user = user
        self.host = host
        self.cwd = HOME_DIR
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "help": self.cmd_help,
            "clear": self.cmd_clear,
            "exit": self.cmd_exit,
        }

    def window_title(self):
        """Заголовок окна, содержащий имя VFS."""
        return f"Эмулятор - [{self.vfs_name}]"

    def banner(self):
        """Приветствие при запуске."""
        return (f"Эмулятор оболочки (VFS: {self.vfs_name}). "
                "Введите 'help' для списка команд.")

    def prompt(self):
        """Строка приглашения в стиле UNIX."""
        return f"{self.user}@{self.host}:{self.cwd}$ "

    def execute(self, line):
        """Разбирает и выполняет строку, возвращает Result."""
        try:
            argv = parse_line(line)
        except ParseError as exc:
            return Result(err=f"shell: ошибка разбора: {exc}\n")
        if not argv:
            return Result()
        handler = self.commands.get(argv[0])
        if handler is None:
            return Result(err=f"{argv[0]}: команда не найдена\n")
        return handler(argv[1:])

    def cmd_ls(self, args):
        """Заглушка ls: печатает имя команды и аргументы."""
        return Result(out=f"ls: {args}\n")

    def cmd_cd(self, args):
        """Заглушка cd: печатает имя команды и аргументы."""
        return Result(out=f"cd: {args}\n")

    def cmd_help(self, args):
        """Выводит список доступных команд."""
        names = ", ".join(sorted(self.commands))
        return Result(out=f"Доступные команды: {names}\n")

    def cmd_clear(self, args):
        """Просит очистить экран."""
        return Result(clear_requested=True)

    def cmd_exit(self, args):
        """Просит завершить работу эмулятора."""
        return Result(exit_requested=True)
