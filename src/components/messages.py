from rich.markdown import Markdown
from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import ListItem, Static

from gvars import Strings


class MessageItem(ListItem):
    """A message item (ListItem) for use in the message log."""

    # Override Default CSS for ListItem to disable the background colour (both for highlighted and non-highlighted)
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

    def __init__(self, source_message: str, allow_markup=False) -> None:
        super().__init__()
        self.source_message = source_message
        self.content_style_overrides = {}
        self.allow_markup = allow_markup

    def compose(
        self,
    ) -> ComposeResult:
        yield self._apply_styles(
            Static(renderable=self.source_message, markup=self.allow_markup)
        )

    def as_item(self) -> MessageItem:
        """Return a MessageItem for this message.

        :return: A MessageItem for this message
        """
        return MessageItem(self)

    def _apply_styles(self, content: Static) -> Static:
        """Apply the content style overrides to the content.

        :param content: The content to apply the styles to
        :return: The content with the styles applied, for chaining
        """
        for key, value in self.content_style_overrides.items():
            content.styles.__setattr__(key, value)
        return content

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.source_message}'>"

    def __str__(self) -> str:
        return self.source_message


class MarkdownMessage(GenericMessage):
    """A variant of GenericMessage that will process the message as Markdown. Ignores allow_markup."""

    def compose(self) -> ComposeResult:
        yield self._apply_styles(Static(renderable=Markdown(self.source_message)))


class TextMessage(MarkdownMessage):
    """A message that contains text and a sender. Markdown supported."""

    def __init__(self, sender: str, message: str) -> None:
        self.sender = sender
        self.message = message
        super().__init__(
            Strings.UI.MessageTypes.TEXT.format(sender=sender, message=message)
        )


class MOTDMessage(GenericMessage):
    """A message that contains the message of the day from a server."""

    def __init__(self, message: str) -> None:
        super().__init__(
            Strings.UI.MessageTypes.MOTD.format(message=escape(message)),
            allow_markup=True,
        )

        self.content_style_overrides = {
            "text_align": "center",
            "text_style": "overline underline",
        }


class EventMessage(GenericMessage):
    """A message that contains an event notification message."""

    def __init__(self, message: str) -> None:
        super().__init__(Strings.UI.MessageTypes.EVENT.format(message=message))

        self.content_style_overrides = {
            "color": "gray",
            "text_style": "italic",
        }


class ServerMessage(GenericMessage):
    """A message that contains a server message."""

    def __init__(self, message: str) -> None:
        super().__init__(
            Strings.UI.MessageTypes.SERVER.format(message=escape(message)),
            allow_markup=True,
        )

        self.content_style_overrides = {"color": "gray"}


class SystemMessage(GenericMessage):
    """A message that contains a system message. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(
            Strings.UI.MessageTypes.SYSTEM.format(message=message), allow_markup=True
        )

        self.content_style_overrides = {"color": "gray"}


class WarnMessage(GenericMessage):
    """A message that contains a warning message. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(
            Strings.UI.MessageTypes.WARN.format(message=message), allow_markup=True
        )


class ErrorMessage(GenericMessage):
    """A message that contains an error message. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(
            Strings.UI.MessageTypes.ERROR.format(message=message), allow_markup=True
        )


class CommandResponseMessage(GenericMessage):
    """A message that contains a response to a command. Markup supported."""

    def __init__(self, message: str) -> None:
        super().__init__(message, allow_markup=True)

        self.content_style_overrides = {
            "background": "gray 25%",
            "text_style": "italic",
        }
