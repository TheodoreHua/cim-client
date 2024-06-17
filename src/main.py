from textual.app import App, ComposeResult
from textual.widgets import Header, ListView

from components import *
from networking import *
from gvars import Strings


class ChatApp(App):
    def __init__(self, network_handler: GenericHandler = None, username=None) -> None:
        super().__init__()
        # noinspection PyTypeChecker
        self.title = Strings.TITLE
        self.username = username

        self.messages_lv = ListView()
        self.messages_lv.index = None

        self.network_handler = network_handler

        # Register handlers
        if self.network_handler is not None:
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
                "display_error",
                lambda message: self.call_from_thread(
                    lambda: self.add_message(ErrorMessage(message))
                ),
            )
            self.network_handler.subscribe(
                "handle_error", lambda: print("Temporary error handler called.")
            )
            self.network_handler.subscribe(
                "handle_fatal_error",
                lambda: print("Temporary fatal error handler called."),
            )

    def on_mount(self):
        self.network_handler.connect(
            self.username
        )  # avoid problems arising from app not running yet

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.messages_lv
        yield TextBar()

    def add_message(self, message: GenericMessage):
        self.messages_lv.append(message.as_item())
        self.messages_lv.scroll_end()

    def handle_command(self, message: str) -> str:
        """Handle a command entered by the user

        :param message: The raw message entered by the user (including the command prefix)
        :return: A string to process as the new message, or None if there is nothing to send (command was private/handled)
        """
        pass


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
