VERSION = "0.0.1"  # The version of the client


class Strings:  # TODO: Reformat
    """Global strings for the application."""

    class UI:
        TITLE = f"CIM Chat (v{VERSION})"

        LEGACY_WINDOWS_WARNING = "It appears you are running on a legacy version of the Windows console. This is not supported, and may cause visual issues with the application. It is recommended to use a modern terminal emulator such as [link=https://github.com/microsoft/terminal#installing-and-running-windows-terminal]Windows Terminal[/link]."

        TEXT_BAR_PLACEHOLDER = "Type your message here..."
        TEXT_BAR_DISABLED_PLACEHOLDER = (
            "You are currently disconnected from the server."
        )

        MESSAGE_TOO_LONG_PRE_SEND = "Your message was too long to send, the limit is {max_length:,} characters. Here is your message:\n\n[code]{message}[/code]"

        COMMAND_NOT_FOUND = "Command [italic]/{command}[/] [yellow]not found[/]. Use [underline italic]/help[/] to see a list of commands."

        class MessageTypes:
            TEXT = "{sender}: {message}"  # markdown supported
            MOTD = "[bold]MOTD[/]: [italic]{message}[/]"  # markup supported, center-aligned, overlined, underlined
            EVENT = "EVENT | {message}"  # gray, italic
            SERVER = "[bold cyan]SERVER[/] | {message}"  # markup supported, gray
            SYSTEM = "[bold blue]SYSTEM[/] | {message}"  # markup supported, gray
            WARN = "[blink bold yellow]WARN[/] | [bright_yellow]{message}[/]"  # markup supported
            ERROR = "[blink bold bright_red]ERROR[/] | [red]{message}[/]"  # markup supported

    class Server:
        _TEMPORARY_USERNAME = " You have been assigned [underline italic]{username}[/] as your temporary username. You can change it with [underline italic]/nick <new username>[/]."
        _NO_CHANGE = " Your username has not changed."

        USERNAME_REQUIREMENTS_MESSAGE = "Your username must be: {requirements}."
        USERNAME_INITIAL_INVALID = (
            "Your [yellow]username was invalid[/]." + _TEMPORARY_USERNAME
        )
        USERNAME_INITIAL_MISSING = (
            "You [yellow]did not provide a username[/]." + _TEMPORARY_USERNAME
        )
        USERNAME_INITIAL_TAKEN = (
            "Your [yellow]username was already taken[/]." + _TEMPORARY_USERNAME
        )
        USERNAME_CHANGE_INVALID = (
            "The username you requested was [yellow]invalid[/]." + _NO_CHANGE
        )
        USERNAME_CHANGE_TAKEN = (
            "The username you requested was [yellow]already taken[/]." + _NO_CHANGE
        )
        USERNAME_CHANGE_UNKNOWN_ERROR = (
            "An [red]unknown error[/] occurred while changing your username."
            + _NO_CHANGE
        )
        USERNAME_CHANGE_EVENT = "{old}'s username has been changed to {new}."

        CONNECTION_ESTABLISHED = "[green]Connected[/] to server."
        CONNECTION_DROPPED = "[red]Disconnected[/] from server."

        USER_CONNECTED = "{username} has connected to the server."
        USER_DISCONNECTED = "{username} has disconnected from the server."
