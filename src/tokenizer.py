"""Разбор командной строки на аргументы с учётом кавычек."""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
WHITESPACE = " \t"
QUOTES = (SINGLE_QUOTE, DOUBLE_QUOTE)
DOUBLE_ESCAPABLE = (DOUBLE_QUOTE, BACKSLASH)


class ParseError(Exception):
    """Ошибка разбора командной строки."""


class Tokenizer:
    """Конечный автомат, разбивающий строку на аргументы.

    Правила разбора:
      * 'одинарные' кавычки сохраняют всё внутри буквально;
      * "двойные" кавычки допускают экранирование \\" и \\\\;
      * вне кавычек обратный слеш экранирует следующий символ;
      * пустые кавычки дают пустой аргумент;
      * соседние части склеиваются в один аргумент: a"b c"d.
    """

    def __init__(self, line):
        """Подготавливает разбор строки ``line``."""
        self.line = line
        self.pos = 0
        self.args = []
        self.current = []
        self.in_token = False
        self.quote = None

    def run(self):
        """Возвращает список аргументов или бросает ParseError."""
        while self.pos < len(self.line):
            self.step(self.line[self.pos])
            self.pos += 1
        if self.quote is not None:
            raise ParseError(f"незакрытая кавычка {self.quote}")
        self.flush()
        return self.args

    def peek(self):
        """Возвращает следующий символ или пустую строку в конце."""
        following = self.pos + 1
        if following < len(self.line):
            return self.line[following]
        return ""

    def advance(self):
        """Сдвигает позицию на один символ вперёд."""
        self.pos += 1

    def add_char(self, char):
        """Добавляет символ к текущему аргументу."""
        self.current.append(char)
        self.in_token = True

    def flush(self):
        """Завершает текущий аргумент, если он начат."""
        if self.in_token:
            self.args.append("".join(self.current))
        self.current = []
        self.in_token = False

    def step(self, char):
        """Обрабатывает символ в зависимости от состояния кавычек."""
        if self.quote == SINGLE_QUOTE:
            self.step_single(char)
        elif self.quote == DOUBLE_QUOTE:
            self.step_double(char)
        else:
            self.step_plain(char)

    def step_single(self, char):
        """Символ внутри одинарных кавычек."""
        if char == SINGLE_QUOTE:
            self.quote = None
        else:
            self.current.append(char)

    def step_double(self, char):
        """Символ внутри двойных кавычек."""
        if char == DOUBLE_QUOTE:
            self.quote = None
        elif char == BACKSLASH and self.peek() in DOUBLE_ESCAPABLE:
            self.advance()
            self.current.append(self.line[self.pos])
        else:
            self.current.append(char)

    def step_plain(self, char):
        """Символ вне кавычек."""
        if char in WHITESPACE:
            self.flush()
        elif char in QUOTES:
            self.quote = char
            self.in_token = True
        elif char == BACKSLASH:
            self.step_escape()
        else:
            self.add_char(char)

    def step_escape(self):
        """Обрабатывает обратный слеш вне кавычек."""
        if not self.peek():
            raise ParseError("обратный слеш в конце строки")
        self.advance()
        self.add_char(self.line[self.pos])


def parse_line(line):
    """Разбивает строку ``line`` на список аргументов."""
    return Tokenizer(line).run()
