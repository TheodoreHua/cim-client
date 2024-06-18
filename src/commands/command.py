from typing import Callable, Tuple

from rich.markup import escape


class Command:
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[[list], Tuple[bool, str]],
        argument_doc=None,
    ):
        """A command that can be executed by the user.

        :param name: The name of the command (without the prefix)
        :param argument_doc: A string describing the arguments of the command (e.g. "<arg1> [arg2]")
        :param description: A description of the command
        :param func: The function to call when the command is executed.
            | Parameter: list - arguments of command split by spaces
            | Return: Tuple[bool, str] - bool: whether the message should be sent or displayed locally, str: the message to send or display (empty if no message)
        """
        self.name = name
        self.description = description
        self.func = func
        self.argument_doc = argument_doc

    def execute(self, args: list) -> Tuple[bool, str]:
        """Execute the command with the given arguments.

        :param args: The arguments of the command split by spaces
        :return: Tuple[bool, str] - bool: whether the message should be sent or displayed locally, str: the message to send or display (empty if no message)
        """
        return self.func(args)

    def get_help(self, markup=False) -> str:
        """Get the help message for this command.

        :param markup: Whether markup is enabled
        :return: A string containing the help message
        """
        return f"{'[bold]' if markup else ''}/{self.name}{'[/]' if markup else ''}{f' {escape(self.argument_doc) if markup else self.argument_doc}' if self.argument_doc else ''}: {self.description}"

    def __repr__(self) -> str:
        return f"<Command '{self.name}'>"

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def compile_help_string(commands: list, markup=False) -> str:
        """Get the help string for a list of commands.

        :param commands: The list of commands
        :param markup: Whether to use markup in the help messages
        :return: A string containing the help message for all the commands
        """
        return "\n".join([command.get_help(markup) for command in commands])
