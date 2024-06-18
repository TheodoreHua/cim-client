import re
import shlex
import sys
from random import randint
from time import time
from typing import Tuple, Union, Callable, Any, Awaitable

from rich.console import detect_legacy_windows
from rich.markup import escape
from textual.app import App, ComposeResult
from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.widgets import Header, ListView

from commands import *
from components import *
from gvars import Strings, GITHUB_CLIENT, GITHUB_SERVER
from networking import *


class PaletteCommands(Provider):
    @property
    def _palette_commands(
        self,
    ) -> Tuple[
        Tuple[str, Union[Callable[[], Awaitable[Any]], Callable[[], Any]], str], ...
    ]:
        app = self.app
        assert isinstance(app, ChatApp)
        return (
            (
                "Toggle light/dark mode",
                app.action_toggle_dark,
                "Toggles the application between light mode [why?] and dark mode",
            ),
            (
                "Save chat log",
                app.action_save_chat_log,
                "Saves the current chat log to a file in the current directory",
            ),
            (
                "Quit the application",
                app.action_quit,
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
            # Info Commands
            Command(
                "github",
                "Get the GitHub repository links for the project.",
                lambda _: (
                    False,
                    f"Here are the GitHub links:\n* [link={GITHUB_CLIENT}]Client[/] ({re.sub(r'^https://github.com', '', GITHUB_CLIENT)})\n* [link={GITHUB_SERVER}]Server[/] ({re.sub(r'^https://github.com', '', GITHUB_SERVER)})",
                ),
            ),
            # User Commands
            Command(
                "nick",
                "Change your username.",
                lambda args: (
                    (
                        self.network_handler.update_username(args[0])
                        if len(args) == 1
                        else None
                    ),
                    (False, "" if len(args) == 1 else "Please provide a username"),
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
                    rf"{' '.join(args)} ¯\\\_(ツ)\_/¯",
                ),
                "<message>",
            ),
            Command(
                "flip",
                "Adds a flip to the end of your message",
                lambda args: (
                    True,
                    rf"{' '.join(args)} (╯°□°）╯︵ ┻━┻",
                ),
                "<message>",
            ),
            Command(
                "unflip",
                "Adds an unflip to the end of your message",
                lambda args: (
                    True,
                    rf"{' '.join(args)} ┬─┬ ノ( ゜-゜ノ)",
                ),
                "<message>",
            ),
        ]  # list for easy development
        # noinspection PyUnusedLocal -- help_string is used in the lambda
        help_string = (
            "[bold underline]Available Commands[/]:\n"
            + Command.compile_help_string(
                sorted(commands, key=lambda x: x.name), markup=True
            )
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
        # Warn of legacy Windows console
        if detect_legacy_windows():
            self.add_message(WarnMessage(Strings.UI.LEGACY_WINDOWS_WARNING))

        # Attempt network connection
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
        self.add_message(
            CommandResponseMessage(Strings.UI.CHAT_LOG_SAVED.format(filename=filename))
        )


if __name__ == "__main__":
    import argparse
    import requests

    #
    # # TODO: Streamline startup process, check address validity, etc.
    parser = argparse.ArgumentParser(
        description="CIM (Command [Line] Instant Messenger) Client - a simple chat client in the command line, capable of P2P & server-based messaging."
    )
    parser.add_argument(
        "address",
        type=str,
        help="The address of the server to connect to.",
        metavar="ADDRESS",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="The port of the server to connect to.",
        default=None,
    )
    parser.add_argument(
        "-p2p",
        "--peer-to-peer",
        action="store_true",
        help="Use peer-to-peer messaging instead of the default server-based messaging. (COMING SOON)",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="The username to use when connecting to a server.",
    )
    parser.add_argument(
        "--offline-debug", action="store_true", help=argparse.SUPPRESS
    )  # currently unused
    parser.add_argument(
        "--debug", action="store_true", help=argparse.SUPPRESS
    )  # currently unused

    parse = parser.parse_args(
        args=None if sys.argv[1:] else ["--help"]
    )  # show help if no arguments are provided
    address = parse.address
    port = parse.port

    networking_handler = None

    # noinspection HttpUrlsUsage
    if not (
        address.startswith("http://") or address.startswith("https://")
    ):  # add http:// if not provided
        # noinspection HttpUrlsUsage
        address = "http://" + address
    if address.endswith("/"):  # remove trailing slash
        address = address.rstrip("/")
    if re.search(
        r":\d{4,5}$", address
    ):  # if port has been erroneously added to the address
        address_port = int(address.split(":")[-1])

        # conflicting port numbers
        if port is not None and port != address_port:
            print(
                "Conflicting port numbers have been provided (address & flag). Please provide only one port number."
            )
            exit(1)

        # set port to the one provided in the address, and remove it from the address (added later)
        address = re.sub(r":\d{4,5}$", "", address)
        port = address_port

    # Verify URL is valid
    if not re.fullmatch(
        r"^https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}$", address
    ):
        print(
            "The address provided is not a valid address. Please provide either a domain or an IP address, without a path."
        )
        exit(1)

    # If we have a port, add it to the address
    if port is not None:
        address += f":{port}"

    if parse.peer_to_peer:
        print(
            "Peer-to-peer messaging is not yet supported. If you require this functionality, you may run cim-server in addition to cim-client and connect to it in server mode."
        )
        exit(1)
    else:
        print("Attempting to connect to server...")

        # Initial server connection: health check
        while True:
            try:
                r_health = requests.get(f"{address}/health", timeout=3)
                break
            except requests.exceptions.RequestException:
                # If a port has been specified, or we've already tried the default port, don't try again
                if port is not None or address.endswith(":61824"):
                    print(
                        "The server is not running, please verify your connection and/or try again later."
                    )
                    exit(1)
                else:  # Try the default port
                    print(
                        "Connection failed on HTTP[S] ports, trying application default port (61824)..."
                    )
                    address += ":61824"
        if not r_health.ok or r_health.text != "ok":
            print(
                "The server is either not running or not compatible. Please verify your connection and/or try again later."
            )
            exit(1)

        # Retrieve server type
        try:
            r_type = requests.get(f"{address}/type")
        except requests.exceptions.RequestException:
            print(
                "The server is not running, please verify your connection and/or try again later."
            )
            exit(1)
        if not r_type.ok:
            # We've already checked health, so this is likely not a connection issue
            print(
                "Failed to retrieve the server type, the server is likely incompatible with this client."
            )
            exit(1)

        # Check server type
        type_ = r_type.text
        if type_ != "server":
            if type_ == "p2p":
                print(
                    "The server you are trying to connect to is a peer-to-peer server. Please use the -p2p flag to connect to it."
                )
                # TODO: When P2P is implemented, invisibly switch to P2P mode without user intervention
                exit(1)
            else:
                print(
                    "The server you are trying to connect to is not compatible with this client."
                )
                exit(1)

        # Create the networking handler
        networking_handler = ServerHandler(address)

    app = ChatApp(networking_handler, parse.username)
    app.run()
