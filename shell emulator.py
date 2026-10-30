#!/usr/bin/env python3
"""Эмулятор оболочки UNIX-подобной ОС. Этап 1: REPL (GUI на tkinter).

Запуск:
    python shell_emulator.py [имя_VFS]
"""

import sys
import getpass
import tkinter as tk
from tkinter import font as tkfont


class ParseError(Exception):
    """Ошибка разбора командной строки."""


def parse_line(line: str) -> list[str]:
    """Разбивает строку на аргументы с учётом кавычек.

    - 'одинарные' кавычки: всё внутри — буквально;
    - "двойные" кавычки: внутри работают \\" и \\\\;
    - вне кавычек обратный слеш экранирует следующий символ;
    - пустые кавычки ("" или '') дают пустой аргумент;
    - склейка: ab"c d"'e' -> один аргумент `abc de`.
    """
    args: list[str] = []
    cur: list[str] = []
    in_token = False
    quote = None  # None, "'" или '"'
    i, n = 0, len(line)

    while i < n:
        ch = line[i]
        if quote == "'":
            if ch == "'":
                quote = None
            else:
                cur.append(ch)
        elif quote == '"':
            if ch == '"':
                quote = None
            elif ch == "\\" and i + 1 < n and line[i + 1] in '"\\':
                i += 1
                cur.append(line[i])
            else:
                cur.append(ch)
        else:
            if ch in " \t":
                if in_token:
                    args.append("".join(cur))
                    cur, in_token = [], False
            elif ch in "'\"":
                quote = ch
                in_token = True
            elif ch == "\\":
                if i + 1 >= n:
                    raise ParseError("неожиданный конец строки после '\\'")
                i += 1
                cur.append(line[i])
                in_token = True
            else:
                cur.append(ch)
                in_token = True
        i += 1

    if quote is not None:
        raise ParseError(f"незакрытая кавычка {quote}")
    if in_token:
        args.append("".join(cur))
    return args


class ShellEmulator:
    def __init__(self, root: tk.Tk, vfs_name: str):
        self.root = root
        self.vfs_name = vfs_name
        self.user = getpass.getuser()
        self.host = "emulator"
        self.cwd = "~"
        self.history: list[str] = []
        self.hist_pos = 0

        root.title(f"Эмулятор - [{vfs_name}]")
        root.geometry("820x520")

        mono = tkfont.Font(family="Courier", size=12)
        self.text = tk.Text(
            root, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#ffffff",
            font=mono, wrap="char", undo=False, padx=6, pady=6,
            selectbackground="#264f78",
        )
        scroll = tk.Scrollbar(root, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.text.tag_configure("prompt", foreground="#6a9955")
        self.text.tag_configure("error", foreground="#f44747")

        self.text.bind("<Key>", self.on_key)
        self.text.bind("<Return>", self.on_return)
        self.text.bind("<BackSpace>", self.on_backspace)
        self.text.bind("<Left>", self.on_left)
        self.text.bind("<Home>", self.on_home)
        self.text.bind("<Up>", self.on_up)
        self.text.bind("<Down>", self.on_down)
        self.text.bind("<Control-l>", self.on_clear)
        self.text.bind("<<Paste>>", self.on_paste)

        self.write(f"Эмулятор оболочки (VFS: {vfs_name}). "
                   "Введите 'help' для списка команд.\n")
        self.show_prompt()
        self.text.focus_set()

    # ---------- вывод ----------
    def prompt_str(self) -> str:
        return f"{self.user}@{self.host}:{self.cwd}$ "

    def write(self, s: str, tag: str | None = None) -> None:
        self.text.insert("end", s, tag) if tag else self.text.insert("end", s)
        self.text.see("end")

    def show_prompt(self) -> None:
        self.write(self.prompt_str(), "prompt")
        self.text.mark_set("input_start", "end-1c")
        self.text.mark_gravity("input_start", "left")
        self.text.mark_set("insert", "end")
        self.text.see("end")

    def current_input(self) -> str:
        return self.text.get("input_start", "end-1c")

    def set_input(self, s: str) -> None:
        self.text.delete("input_start", "end-1c")
        self.text.insert("end", s)
        self.text.mark_set("insert", "end")

    # ---------- обработка клавиш ----------
    def on_key(self, event):
        if event.state & 0x4:  # Ctrl: копирование и т.п.
            return None
        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R",
                            "Alt_L", "Alt_R", "Left", "Right", "Up", "Down",
                            "Home", "End", "Prior", "Next"):
            return None
        if self.text.compare("insert", "<", "input_start"):
            self.text.mark_set("insert", "end")
        return None

    def on_backspace(self, event):
        if self.text.tag_ranges("sel"):
            return "break"
        if self.text.compare("insert", "<=", "input_start"):
            return "break"
        return None

    def on_left(self, event):
        if self.text.compare("insert", "<=", "input_start"):
            return "break"
        return None

    def on_home(self, event):
        self.text.mark_set("insert", "input_start")
        return "break"

    def on_paste(self, event):
        if self.text.compare("insert", "<", "input_start"):
            self.text.mark_set("insert", "end")
        return None

    def on_up(self, event):
        if self.history and self.hist_pos > 0:
            self.hist_pos -= 1
            self.set_input(self.history[self.hist_pos])
        return "break"

    def on_down(self, event):
        if self.hist_pos < len(self.history) - 1:
            self.hist_pos += 1
            self.set_input(self.history[self.hist_pos])
        else:
            self.hist_pos = len(self.history)
            self.set_input("")
        return "break"

    def on_clear(self, event):
        self.text.delete("1.0", "end")
        self.show_prompt()
        return "break"

    def on_return(self, event):
        line = self.current_input()
        self.write("\n")
        if line.strip():
            self.history.append(line)
        self.hist_pos = len(self.history)
        self.execute(line)
        if self.root.winfo_exists():
            self.show_prompt()
        return "break"

    # ---------- REPL ----------
    def execute(self, line: str) -> None:
        if not line.strip():
            return
        try:
            argv = parse_line(line)
        except ParseError as e:
            self.write(f"shell: ошибка разбора: {e}\n", "error")
            return
        if not argv:
            return
        cmd, args = argv[0], argv[1:]

        handler = getattr(self, f"cmd_{cmd}", None)
        if handler is None:
            self.write(f"{cmd}: команда не найдена\n", "error")
            return
        handler(args)

    # ---------- команды (заглушки) ----------
    def cmd_ls(self, args: list[str]) -> None:
        self.write(f"ls: {args}\n")

    def cmd_cd(self, args: list[str]) -> None:
        self.write(f"cd: {args}\n")

    def cmd_help(self, args: list[str]) -> None:
        self.write("Доступные команды: ls, cd, help, clear, exit\n")

    def cmd_clear(self, args: list[str]) -> None:
        self.text.delete("1.0", "end")

    def cmd_exit(self, args: list[str]) -> None:
        self.root.destroy()


def main() -> None:
    vfs_name = sys.argv[1] if len(sys.argv) > 1 else "vfs"
    root = tk.Tk()
    ShellEmulator(root, vfs_name)
    root.mainloop()


if __name__ == "__main__":
    main()
