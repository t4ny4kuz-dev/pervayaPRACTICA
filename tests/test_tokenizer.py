"""Тесты парсера аргументов с кавычками."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tokenizer import ParseError, parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки функции parse_line."""

    def test_plain_words(self):
        """Обычные слова делятся по пробелам и табам."""
        self.assertEqual(parse_line("ls  -l\t/tmp"), ["ls", "-l", "/tmp"])

    def test_empty_line(self):
        """Пустая и пробельная строки дают пустой список."""
        self.assertEqual(parse_line(""), [])
        self.assertEqual(parse_line("   "), [])

    def test_double_quotes(self):
        """Двойные кавычки сохраняют пробелы."""
        self.assertEqual(parse_line('ls "my dir"'), ["ls", "my dir"])

    def test_single_quotes(self):
        """Одинарные кавычки сохраняют всё буквально."""
        self.assertEqual(parse_line("echo 'a \"b\" \\n'"),
                         ["echo", 'a "b" \\n'])

    def test_empty_argument(self):
        """Пустые кавычки дают пустой аргумент."""
        self.assertEqual(parse_line('cmd "" \'\''), ["cmd", "", ""])

    def test_concatenation(self):
        """Соседние части склеиваются в один аргумент."""
        self.assertEqual(parse_line('x"y z"\'w\''), ["xy zw"])

    def test_escapes_in_double_quotes(self):
        """В двойных кавычках работают \\" и \\\\."""
        self.assertEqual(parse_line('echo "a\\"b\\\\c"'),
                         ["echo", 'a"b\\c'])

    def test_backslash_outside_quotes(self):
        """Вне кавычек слеш экранирует пробел."""
        self.assertEqual(parse_line("cd my\\ dir"), ["cd", "my dir"])

    def test_unclosed_quote(self):
        """Незакрытая кавычка вызывает ParseError."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')

    def test_trailing_backslash(self):
        """Слеш в конце строки вызывает ParseError."""
        with self.assertRaises(ParseError):
            parse_line("ls abc\\")


if __name__ == "__main__":
    unittest.main()
