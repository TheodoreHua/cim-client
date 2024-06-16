from typing import TYPE_CHECKING

from textual import events
from textual.widgets import Input

from .messages import *

if TYPE_CHECKING:  # avoid cyclic imports while allowing for type checking
    from src.main import ChatApp


class TextBar(Input, can_focus=True):
    app: 'ChatApp'

    def on_mount(self, event: events.Mount) -> None:
        self.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if not message:
            return

        if message.startswith("/"):
            # TODO: Handle commands
            pass

        # TODO
        self.app.handle_message(TextMessage(message, self.app.username))

        self.value = ""
