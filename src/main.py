from textual.app import App, ComposeResult
from textual.widgets import Header, ListView

from components import *
from networking import *
from gvars import Strings


class ChatApp(App):
    def __init__(self) -> None:
        super().__init__()
        # noinspection PyTypeChecker
        self.title = Strings.TITLE
        self.username = "Anonymous"

        self.messages_lv = ListView()
        self.messages_lv.index = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.messages_lv
        yield TextBar()

    def handle_message(self, message: GenericMessage):
        item = message.as_item()
        self.messages_lv.append(item)
        self.messages_lv.scroll_end()


if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser(description="CIM (Command [Line] Instant Messenger) Client - a simple chat client for the command line, capable of P2P & server-based messaging.")
    #
    # parse = parser.parse_args()
    app = ChatApp()
    app.run()
