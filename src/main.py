"""Точка входа: запуск графического эмулятора оболочки."""

import argparse
import getpass
import tkinter as tk

from gui import ShellWindow
from shell import Shell

DEFAULT_VFS = "vfs"


def parse_args(argv=None):
    """Разбирает аргументы командной строки приложения."""
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX-подобной ОС (GUI)."
    )
    parser.add_argument(
        "--vfs", default=DEFAULT_VFS,
        help="имя виртуальной файловой системы (в заголовке окна)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Создаёт окно и запускает цикл событий."""
    args = parse_args(argv)
    shell = Shell(args.vfs, getpass.getuser())
    root = tk.Tk()
    ShellWindow(root, shell)
    root.mainloop()


if __name__ == "__main__":
    main()
