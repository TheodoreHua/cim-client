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

    def __init__(self, display_message: str) -> None:
        super().__init__()
        self.display_message = display_message
        self.content_style_overrides = {}

    def compose(self) -> ComposeResult:
        content = Static(renderable=self.display_message, markup=False)
        for key, value in self.content_style_overrides.items():
            content.styles.__setattr__(key, value)

        yield content

    def as_item(self) -> MessageItem:
        return MessageItem(self)


class TextMessage(GenericMessage):
    """A message that contains text and a sender."""
    def __init__(self, message: str, sender: str) -> None:
        self.message = message
        self.sender = sender
        super().__init__(f"{self.sender}: {self.message}")


class FormattedTextMessage(TextMessage):
    """A message that contains formatted text and a sender."""
    def __init__(self, message: str, sender: str) -> None:
        # TODO: Handle formatting
        super().__init__(message, sender)

    def compose(self) -> ComposeResult:
        yield Static(renderable=self.display_message, markup=True)


class MOTDMessage(GenericMessage):
    """A message that contains the message of the day from a server."""
    def __init__(self, message: str) -> None:
        super().__init__(f"MOTD: {message}")

        self.content_style_overrides = {
            "text_align": "center",
            "text_style": "italic underline"
        }


class EventMessage(GenericMessage):
    """A message that contains an event notification message."""
    def __init__(self, message: str) -> None:
        super().__init__(f"EVENT | {message}")

        self.content_style_overrides = {
            "color": "gray",
            "text_style": "italic",
        }


class SystemMessage(GenericMessage):
    """A message that contains a system message."""
    def __init__(self, message: str) -> None:
        super().__init__(f"SYSTEM | {message}")

        self.content_style_overrides = {
            "color": "gray"
        }


class ErrorMessage(GenericMessage):
    """A message that contains an error message."""
    def __init__(self, message: str) -> None:
        super().__init__(f"ERROR | {message}")

        self.content_style_overrides = {
            "color": "red",
            "text_style": "bold",
        }


class CommandResponseMessage(GenericMessage):
    """A message that contains a response to a command."""
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.content_style_overrides = {
            "background": "gray",
            "text_style": "italic"
        }
