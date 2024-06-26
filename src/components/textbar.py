from typing import TYPE_CHECKING

from rich.markup import escape
from textual.widgets import Input

from components.messages import CommandResponseMessage
from gvars import Strings

if TYPE_CHECKING:  # avoid cyclic imports while allowing for type checking
    from src.main import ChatApp


class TextBar(Input, can_focus=True):
    """The input bar for the ChatApp."""

    app: "ChatApp"

    def __init__(self, *args, **kwargs):
        super().__init__(validate_on=["changed"], *args, **kwargs)
        self.placeholder = Strings.UI.TEXT_BAR_PLACEHOLDER
        self.max_message_length = None

    def on_mount(self) -> None:
        """Focus on the input bar by default. (Called when the component is mounted)"""
        self.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle the input submission event.

        :param event: The input submission event
        """
        message = event.value.strip()
        if message.startswith("/"):
            message = self.app.handle_command(message).strip()

        # Check the message length before sending, as the restrict *can* be bypassed
        if self.max_message_length and len(message) > self.max_message_length:
            self.app.add_message(
                CommandResponseMessage(
                    Strings.UI.MESSAGE_TOO_LONG_PRE_SEND.format(
                        max_length=self.max_message_length, message=escape(message)
                    )
                )
            )
        elif message:
            self.app.network_handler.send_message(message)

        self.value = ""

    def enable(self):
        """Enable the text bar, and set the placeholder to the default placeholder."""
        # noinspection PyTypeChecker
        self.disabled = False
        self.placeholder = Strings.UI.TEXT_BAR_PLACEHOLDER

    def disable(self):
        """Disable the text bar, and set the placeholder to the disabled placeholder."""
        # noinspection PyTypeChecker
        self.disabled = True
        self.placeholder = Strings.UI.TEXT_BAR_DISABLED_PLACEHOLDER

    def set_length_limit(self, limit: int):
        """Set the maximum message length.

        :param limit: The maximum message length, in characters. Set to -1 for no limit.
        """
        limit = None if limit == -1 else limit
        self.max_message_length = limit
        self.restrict = None if limit is None else rf"^(\/.*|.{{0,{limit}}})$"
