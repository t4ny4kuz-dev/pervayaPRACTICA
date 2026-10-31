"""Тесты ядра оболочки (REPL без GUI)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shell import Shell


class ShellTest(unittest.TestCase):
    """Проверки класса Shell."""

    def setUp(self):
        """Создаёт оболочку для каждого теста."""
        self.shell = Shell("myvfs", "user")

    def test_title_contains_vfs_name(self):
        """Заголовок окна содержит имя VFS."""
        self.assertIn("myvfs", self.shell.window_title())

    def test_prompt(self):
        """Приглашение выглядит как в UNIX."""
        self.assertEqual(self.shell.prompt(), "user@emulator:~$ ")

    def test_stub_prints_arguments(self):
        """Заглушка ls печатает аргументы после разбора кавычек."""
        result = self.shell.execute("ls -l 'a b'")
        self.assertEqual(result.out, "ls: ['-l', 'a b']\n")

    def test_cd_stub(self):
        """Заглушка cd печатает аргументы."""
        self.assertEqual(self.shell.execute("cd /").out, "cd: ['/']\n")

    def test_unknown_command(self):
        """Неизвестная команда даёт сообщение об ошибке."""
        result = self.shell.execute("foo")
        self.assertIn("команда не найдена", result.err)

    def test_parse_error_reported(self):
        """Ошибка парсера выводится, а не падает."""
        result = self.shell.execute('ls "abc')
        self.assertIn("ошибка разбора", result.err)

    def test_empty_line(self):
        """Пустая строка ничего не делает."""
        result = self.shell.execute("   ")
        self.assertEqual((result.out, result.err), ("", ""))

    def test_exit_and_clear(self):
        """exit и clear выставляют соответствующие флаги."""
        self.assertTrue(self.shell.execute("exit").exit_requested)
        self.assertTrue(self.shell.execute("clear").clear_requested)


if __name__ == "__main__":
    unittest.main()
