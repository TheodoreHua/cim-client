VERSION = "0.0.1"  # The version of the client


class Strings:
    """Global strings for the application."""

    class UI:
        TITLE = f"CIM Chat (v{VERSION})"
        TEXT_BAR_PLACEHOLDER = "Type your message here..."
        TEXT_BAR_DISABLED_PLACEHOLDER = (
            "You are currently disconnected from the server."
        )
        MESSAGE_TOO_LONG = "Your message was too long to send, the limit is {max_length:,} characters. Here is your message:\n\n[code]{message}[/code]"

        class MessageTypes:
            TEXT = "{sender}: {message}"  # markdown supported
            MOTD = "[bold]MOTD[/]: [italic]{message}[/]"  # markup supported, center-aligned, overlined, underlined
            EVENT = "EVENT | {message}"  # gray, italic
            SERVER = "SERVER | {message}"  # gray
            SYSTEM = "SYSTEM | {message}"  # markup supported, gray
            ERROR = "ERROR | {message}"  # markup supported, red, bold

    # ! SERVER COMMUNICATION
    class Server:
        USERNAME_MISSING = "You did not provide a username. You have been assigned [italic]{username}[/] as your temporary username. You can change it with [italic]/nick <new username>[/]."
        USERNAME_TAKEN = "Your username was [underline]already taken[/]. You have been assigned [italic]{username}[/] as your temporary username. You can change it with [italic]/nick <new username>[/]."
        CONNECTION_ESTABLISHED = "Connected to server."
        CONNECTION_DROPPED = "Disconnected from server."
        USER_CONNECTED = "{username} has connected to the server."
        USER_DISCONNECTED = "{username} has disconnected from the server."
        USERNAME_CHANGE = "{old}'s username has been changed to {new}."
