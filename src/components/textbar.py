from typing import TYPE_CHECKING

from textual.widgets import Input

from gvars import Strings

if TYPE_CHECKING:  # avoid cyclic imports while allowing for type checking
    from src.main import ChatApp


class TextBar(Input, can_focus=True):
    app: "ChatApp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = Strings.TEXT_BAR_PLACEHOLDER

    def on_mount(self) -> None:
        self.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if message.startswith("/"):
            message = self.app.handle_command(message)

        if message:
            self.app.network_handler.send_message(message)

        self.value = ""
