from enum import Enum

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import ListItem, Static


class MessageItem(ListItem):
    DEFAULT_CSS = """
    MessageItem {
        color: $text;
        background: $surface;
        height: auto;
        overflow: hidden hidden;
    }
    
    MessageItem.--highlight {
        background: $surface !important;
    }
    """


class GenericMessage(Container):
    """A generic message that can be displayed in the chat window."""

    def __init__(self, display_message: str, allow_markup=False) -> None:
        super().__init__()
        self.display_message = display_message
        self.content_style_overrides = {}
        self.allow_markup = allow_markup

    def compose(
        self,
    ) -> (
        ComposeResult
    ):  # TODO: Consider horizontal elements? (e.g. sender/type/etc on left, message on right -- would prevent fake sender in message)
        content = Static(renderable=self.display_message, markup=self.allow_markup)
        for key, value in self.content_style_overrides.items():
            content.styles.__setattr__(key, value)

        yield content

    def as_item(self) -> MessageItem:
        return MessageItem(self)


class TextMessage(GenericMessage):
    """A message that contains text and a sender."""

    def __init__(self, sender: str, message: str) -> None:
        self.sender = sender
        self.message = message
        super().__init__(f"{self.sender}: {self.message}")


class MOTDMessage(GenericMessage):
    """A message that contains the message of the day from a server."""

    def __init__(self, message: str) -> None:
        super().__init__(f"MOTD: {message}")

        self.content_style_overrides = {
            "text_align": "center",
            "text_style": "italic underline",
        }


class EventMessage(GenericMessage):
    """A message that contains an event notification message."""

    def __init__(self, message: str) -> None:
        super().__init__(f"EVENT | {message}")

        self.content_style_overrides = {
            "color": "gray",
            "text_style": "italic",
        }


class ServerMessage(GenericMessage):
    """A message that contains a server message."""

    def __init__(self, message: str) -> None:
        super().__init__(f"SERVER | {message}")

        self.content_style_overrides = {"color": "gray"}


class SystemMessage(GenericMessage):
    """A message that contains a system message. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(f"SYSTEM | {message}", allow_markup=True)

        self.content_style_overrides = {"color": "gray"}


class ErrorMessage(GenericMessage):
    """A message that contains an error message. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(f"ERROR | {message}", allow_markup=True)

        self.content_style_overrides = {
            "color": "red",
            "text_style": "bold",
        }


class CommandResponseMessage(GenericMessage):
    """A message that contains a response to a command. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(message, allow_markup=True)

        self.content_style_overrides = {"background": "gray", "text_style": "italic"}
