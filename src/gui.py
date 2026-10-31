"""Графический интерфейс эмулятора оболочки на tkinter."""

import tkinter as tk
from tkinter import font as tkfont

WINDOW_SIZE = "820x520"
FONT_FAMILY = "Courier"
FONT_SIZE = 12
INPUT_MARK = "input_start"
CONTROL_MASK = 0x4
NAVIGATION_KEYS = (
    "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
    "Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next",
)
COLORS = {
    "bg": "#1e1e1e",
    "fg": "#d4d4d4",
    "prompt": "#6a9955",
    "error": "#f44747",
    "select": "#264f78",
}


class ShellWindow:
    """Окно терминала, связывающее tkinter и ядро Shell."""

    def __init__(self, root, shell):
        """Строит окно и показывает первое приглашение."""
        self.root = root
        self.shell = shell
        self.history = []
        self.hist_pos = 0
        root.title(shell.window_title())
        root.geometry(WINDOW_SIZE)
        self.text = self.build_text()
        self.bind_keys()
        self.write(shell.banner() + "\n")
        self.show_prompt()
        self.text.focus_set()

    def build_text(self):
        """Создаёт текстовое поле с полосой прокрутки."""
        mono = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        text = tk.Text(
            self.root, bg=COLORS["bg"], fg=COLORS["fg"], font=mono,
            insertbackground=COLORS["fg"], wrap="char", padx=6,
            pady=6, selectbackground=COLORS["select"],
        )
        scroll = tk.Scrollbar(self.root, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)
        text.tag_configure("prompt", foreground=COLORS["prompt"])
        text.tag_configure("error", foreground=COLORS["error"])
        return text

    def bind_keys(self):
        """Привязывает обработчики клавиш."""
        handlers = {
            "<Key>": self.on_key,
            "<Return>": self.on_return,
            "<BackSpace>": self.on_backspace,
            "<Delete>": self.on_backspace,
            "<Left>": self.on_left,
            "<Home>": self.on_home,
            "<Up>": self.on_up,
            "<Down>": self.on_down,
            "<Control-l>": self.on_clear,
            "<<Paste>>": self.on_paste,
        }
        for sequence, handler in handlers.items():
            self.text.bind(sequence, handler)

    def write(self, string, *tags):
        """Дописывает текст в конец окна."""
        self.text.insert("end", string, tags)
        self.text.see("end")

    def show_prompt(self):
        """Печатает приглашение и ставит границу ввода."""
        self.write(self.shell.prompt(), "prompt")
        self.text.mark_set(INPUT_MARK, "end-1c")
        self.text.mark_gravity(INPUT_MARK, "left")
        self.text.mark_set("insert", "end")
        self.text.see("end")

    def current_input(self):
        """Возвращает введённую пользователем строку."""
        return self.text.get(INPUT_MARK, "end-1c")

    def set_input(self, string):
        """Заменяет введённую строку (для истории команд)."""
        self.text.delete(INPUT_MARK, "end-1c")
        self.text.insert("end", string)
        self.text.mark_set("insert", "end")

    def before_input(self):
        """Истина, если курсор стоит левее границы ввода."""
        return self.text.compare("insert", "<", INPUT_MARK)

    def keep_cursor_in_input(self):
        """Возвращает курсор в строку ввода."""
        if self.before_input():
            self.text.tag_remove("sel", "1.0", "end")
            self.text.mark_set("insert", "end")

    def on_key(self, event):
        """Обычное нажатие клавиши."""
        if event.state & CONTROL_MASK:
            return None
        if event.keysym not in NAVIGATION_KEYS:
            self.keep_cursor_in_input()
        return None

    def on_paste(self, event):
        """Вставка из буфера обмена."""
        self.keep_cursor_in_input()
        return None

    def on_backspace(self, event):
        """Запрещает стирать вывод и приглашение."""
        at_border = self.text.compare("insert", "<=", INPUT_MARK)
        if self.text.tag_ranges("sel") or at_border:
            return "break"
        return None

    def on_left(self, event):
        """Запрещает уходить курсором левее приглашения."""
        if self.text.compare("insert", "<=", INPUT_MARK):
            return "break"
        return None

    def on_home(self, event):
        """Home переносит курсор к началу ввода."""
        self.text.mark_set("insert", INPUT_MARK)
        return "break"

    def on_up(self, event):
        """Предыдущая команда из истории."""
        if self.hist_pos > 0:
            self.hist_pos -= 1
            self.set_input(self.history[self.hist_pos])
        return "break"

    def on_down(self, event):
        """Следующая команда из истории."""
        last_index = len(self.history) - 1
        if self.hist_pos < last_index:
            self.hist_pos += 1
            self.set_input(self.history[self.hist_pos])
        else:
            self.hist_pos = len(self.history)
            self.set_input("")
        return "break"

    def on_clear(self, event):
        """Ctrl+L очищает экран."""
        self.clear_screen()
        self.show_prompt()
        return "break"

    def clear_screen(self):
        """Удаляет весь текст из окна."""
        self.text.delete("1.0", "end")

    def on_return(self, event):
        """Выполняет введённую строку и показывает результат."""
        line = self.current_input()
        self.write("\n")
        if line.strip():
            self.history.append(line)
        self.hist_pos = len(self.history)
        result = self.shell.execute(line)
        self.show_result(result)
        return "break"

    def show_result(self, result):
        """Выводит результат команды и новое приглашение."""
        if result.clear_requested:
            self.clear_screen()
        if result.out:
            self.write(result.out)
        if result.err:
            self.write(result.err, "error")
        if result.exit_requested:
            self.root.destroy()
        else:
            self.show_prompt()
