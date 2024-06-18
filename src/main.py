import shlex
from random import randint
from time import time
from typing import Union, Callable, Awaitable, Any

from rich.console import detect_legacy_windows
from rich.markup import escape
from textual.app import App, ComposeResult
from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.widgets import Header, ListView

from commands import *
from components import *
from gvars import Strings
from networking import *


class PaletteCommands(Provider):
    @property
    def _palette_commands(self) -> tuple[tuple[str, Union[Callable[[], Awaitable[Any]], Callable[[], Any]], str], ...]:
        return (
            (
                "Toggle light/dark mode",
                self.app.action_toggle_dark,
                "Toggles the application between light mode [why?] and dark mode",
            ),
            (
                "Save chat log",
                self.app.action_save_chat_log,
                "Saves the current chat log to a file in the current directory",
            ),
            (
                "Quit the application",
                self.app.action_quit,
                "Quits the application",
            ),
        )

    async def discover(self) -> Hits:
        """Handle a request for the discovery commands for this provider.

        Yields:
            Commands that can be discovered.
        """
        for name, runnable, help_text in self._palette_commands:
            yield DiscoveryHit(
                name,
                runnable,
                help=help_text,
            )

    async def search(self, query: str) -> Hits:
        app = self.app
        assert isinstance(app, ChatApp)

        matcher = self.matcher(query)
        for name, runnable, help_text in self._palette_commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    runnable,
                    help=help_text,
                )


class ChatApp(App):
    """The main application for the CIM client."""
    COMMANDS = {PaletteCommands}

    def __init__(self, network_handler: GenericHandler = None, username=None) -> None:
        """Create a new ChatApp instance

        :param network_handler: The network handler to use for communication
        :param username: The username to use when connecting to the server, or None for server default
        """
        super().__init__()
        # noinspection PyTypeChecker
        self.title = Strings.UI.TITLE
        self.username = username
        self.network_handler = network_handler

        # Message Log (ListView of MessageItems)
        self.messages_lv = ListView()

        # Message Bar
        self.text_bar = TextBar()

        # Initialize the supported commands
        self.commands = {}
        self.init_commands()

        # Register [network handler] [event handlers], if we have a network handler
        if self.network_handler is not None:
            self.init_network_handler_subscriptions()

    def init_commands(self):
        """Initialize all supported commands"""
        commands = [
            # Management Commands
            Command(
                "quit",
                "Quit the application.",
                lambda _: (self.exit(), (False, ""))[1],
            ),
            Command(
                "online",
                "List all online users.",
                lambda _: (
                    False,
                    "Online Users:\n" + "\n".join(self.network_handler.get_online()),
                ),
            ),
            # User Commands
            Command(
                "nick",
                "Change your username.",
                lambda args: (
                    self.network_handler.update_username(args[0]),
                    (False, ""),
                )[1],
                "<new username>",
            ),
            Command(
                "clear",
                "Clear the message log.",
                lambda _: (self.messages_lv.clear(), (False, ""))[1],
            ),
            # Internal Utility Commands
            Command(
                "roll",
                "Roll a die",
                lambda args: (
                    False,
                    (
                        f"Your d{int(args[0])} roll: {randint(1, int(args[0])):,}"
                        if len(args) == 1 and args[0].isnumeric() and int(args[0]) > 0
                        else f"Your d6 roll: {randint(1, 6)}"
                    ),
                ),
                "[sides]",
            ),
            # Message Utility & Emote Commands
            Command(
                "me",
                "Sends a message as an action (italicized)",
                lambda args: (True, f"_{' '.join(args)}_"),
            ),
            Command(
                "shrug",
                "Adds a shrug to the end of your message",
                lambda args: (
                    True,
                    rf"{' '.join(args) + (' ' if len(args) > 0 else '')}¯\\\_(ツ)\_/¯",
                ),
                "<message>",
            ),
            Command(
                "flip",
                "Adds a flip to the end of your message",
                lambda args: (
                    True,
                    rf"{' '.join(args) + (' ' if len(args) > 0 else '')}(╯°□°）╯︵ ┻━┻",
                ),
                "<message>",
            ),
            Command(
                "unflip",
                "Adds an unflip to the end of your message",
                lambda args: (
                    True,
                    rf"{' '.join(args) + (' ' if len(args) > 0 else '')}┬─┬ ノ( ゜-゜ノ)",
                ),
            ),
        ]  # list for easy development
        # noinspection PyUnusedLocal -- help_string is used in the lambda
        help_string = "Available Commands:\n" + Command.compile_help_string(
            sorted(commands, key=lambda x: x.name)
        )
        commands.append(
            Command(
                "help", "Display this help message.", lambda _: (False, help_string)
            )
        )  # help command won't show up in its own output, but who needs to look at the command they're running anyway?
        self.commands = {
            command.name: command for command in commands
        }  # convert to dict for easy access

    def init_network_handler_subscriptions(self):
        """Add all necessary network handler subscriptions"""
        self.network_handler.subscribe(
            "display_message",
            lambda sender, message: self.call_from_thread(
                lambda: self.add_message(TextMessage(sender, message))
            ),
        )
        self.network_handler.subscribe(
            "display_motd",
            lambda message: self.call_from_thread(
                lambda: self.add_message(MOTDMessage(message))
            ),
        )
        self.network_handler.subscribe(
            "display_event",
            lambda message: self.call_from_thread(
                lambda: self.add_message(EventMessage(message))
            ),
        )
        self.network_handler.subscribe(
            "display_server",
            lambda message: self.call_from_thread(
                lambda: self.add_message(ServerMessage(message))
            ),
        )
        self.network_handler.subscribe(
            "display_system",
            lambda message: self.call_from_thread(
                lambda: self.add_message(SystemMessage(message))
            ),
        )
        self.network_handler.subscribe(
            "display_warning",
            lambda message: self.call_from_thread(
                lambda: self.add_message(WarnMessage(message))
            ),
        )
        self.network_handler.subscribe(
            "display_error",
            lambda message, fatal=False: self.call_from_thread(
                lambda: self.add_message(ErrorMessage(message, fatal))
            ),
        )
        self.network_handler.subscribe(
            "handle_reconnect", lambda: self.call_from_thread(self.text_bar.enable)
        )
        self.network_handler.subscribe(
            "handle_disconnect",
            lambda: self.call_from_thread(self.text_bar.disable),
        )
        self.network_handler.subscribe(
            "handle_error",
            lambda type_: self.call_from_thread(lambda: self.handle_error(type_)),
        )
        self.network_handler.subscribe(
            "handle_fatal_error",
            lambda type_: self.call_from_thread(lambda: self.handle_fatal_error(type_)),
        )
        self.network_handler.subscribe("handle_username_update", self.set_username)
        self.network_handler.subscribe(
            "set_length_limit",
            lambda limit: self.call_from_thread(
                lambda: self.text_bar.set_length_limit(limit)
            ),
        )

    def on_mount(self):
        """Called when the application is mounted (ready)"""
        if detect_legacy_windows():
            self.add_message(WarnMessage(Strings.UI.LEGACY_WINDOWS_WARNING))

        # called here to ensure the app is ready for messages
        if not self.network_handler.connect(self.username):
            # Connection failed
            self.add_message(ErrorMessage(Strings.Server.CONNECTION_FAILED, fatal=True))
            self.handle_fatal_error("connection_failed")
            return

    def compose(self) -> ComposeResult:
        """Compose the application layout"""
        yield Header()
        yield self.messages_lv
        yield self.text_bar

    def set_username(self, username: str):
        """Set the username of the client"""
        self.username = username

    def add_message(self, message: GenericMessage):
        """Add a message to the message log"""
        self.messages_lv.append(message.as_item())
        if (
            not self.messages_lv.is_vertical_scrollbar_grabbed
        ):  # if not being manually scrolled, scroll to the bottom
            self.messages_lv.scroll_end(animate=False)

    def handle_command(self, message: str) -> str:
        """Handle a command entered by the user

        :param message: The raw message entered by the user (including the command prefix)
        :return: A string to process as the new message, or empty string if there is nothing to send (command was handled internally)
        """
        # Split into command and arguments
        message = message[1:]  # remove the command prefix
        try:
            command_name, *args = shlex.split(message)
        except ValueError:
            return "Invalid command."

        # Check if the command exists
        if command_name not in self.commands:
            # self.add_message(ErrorMessage(f"Command '{command_name}' not found."))
            self.add_message(
                CommandResponseMessage(
                    Strings.UI.COMMAND_NOT_FOUND.format(command=escape(command_name))
                )
            )
            return ""

        # Execute the command
        command = self.commands[command_name]
        send, message = command.execute(args)
        if message:  # if there is a message to send
            if send:  # and we want to send it
                return message  # then send it
            # otherwise, display it locally
            self.add_message(CommandResponseMessage(message))
        return ""  # no message to send

    def handle_error(self, type_: str):
        """Handles a non-fatal error from the network handler. Notifying is already handled by the network handler."""
        pass  # we don't need to do anything else here

    def handle_fatal_error(self, type_: str):
        """Handles a fatal error from the network handler. Notifying is already handled by the network handler."""
        self.add_message(SystemMessage(Strings.UI.FATAL_ERROR_MESSAGE))
        self.text_bar.disable()

    def action_save_chat_log(self):
        """Save the chat log to a file"""
        chat_log = "\n".join(
            str(message) for message in self.messages_lv.query("TextMessage").results()
        )
        filename = f"chat_log_{int(time())}.txt"
        try:
            with open(filename, "w") as f:
                f.write(chat_log)
        except (Exception,):
            self.add_message(ErrorMessage(Strings.UI.CHAT_LOG_SAVE_FAILED))
            return
        self.add_message(CommandResponseMessage(Strings.UI.CHAT_LOG_SAVED.format(filename=filename)))


if __name__ == "__main__":
    # import argparse
    # import requests
    #
    # # TODO: Streamline startup process, check address validity, etc.
    # parser = argparse.ArgumentParser(description="CIM (Command [Line] Instant Messenger) Client - a simple chat client for the command line, capable of P2P & server-based messaging.")
    # parser.add_argument('address', type=str, nargs='?', help="The address of the server to connect to. Use --server to start a server instead.", metavar='ADDRESS')
    # parser.add_argument('-s', '--server', '--host', action='store_true', help="Start a server instead of connecting to one.")
    # parser.add_argument('-u', '--username', type=str, help="The username to use when connecting to a server.")
    #
    # parse = parser.parse_args()
    # address = parse.address
    #
    # networking_handler = None
    # if address == "debug":
    #     pass  # no networking
    # elif parse.server:
    #     # Start server
    #     exit(1)
    # else:
    #     # noinspection HttpUrlsUsage
    #     try:
    #         r = requests.get(f"{parse.address}/health")
    #     except requests.exceptions.RequestException:
    #         print("Server is not running.")
    #         exit(1)
    #     if not r.ok or r.text != "ok":
    #         print("Server is not running.")
    #         exit(1)
    #     # noinspection HttpUrlsUsage
    #     type_ = requests.get(f"{parse.address}/type").text
    #     if type_ == "server":
    #         networking_handler = ServerHandler(parse.address)
    #     elif type_ == "p2p":
    #         pass
    #     else:
    #         print("Invalid server type.")
    #         exit(1)

    app = ChatApp(ServerHandler("http://127.0.0.1:5000"))
    app.run()
