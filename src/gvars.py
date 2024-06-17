VERSION = "0.0.1"  # The version of the client


class Strings:
    """Global strings for the application."""

    class UI:
        TITLE = f"CIM Chat (v{VERSION})"
        TEXT_BAR_PLACEHOLDER = "Type your message here..."

        class MessageTypes:
            TEXT = "{}: {}"  # markdown supported
            MOTD = "[bold]MOTD:[/]: [italic]{}[/]"  # markup supported, center-aligned, underlined
            EVENT = "EVENT | {}"  # gray, italic
            SERVER = "SERVER | {}"  # gray
            SYSTEM = "SYSTEM | {}"  # markup supported, gray
            ERROR = "ERROR | {}"  # markup supported, red, bold

    # ! SERVER COMMUNICATION
    class Server:
        USERNAME_MISSING = "You did not provide a username. You have been assigned [italic]{}[/] as your temporary username. You can change it with [italic]/nick <new_username>[/]."
        USERNAME_TAKEN = "Your username was [underline]already taken[/underline. You have been assigned [italic]{}[/] as your temporary username. You can change it with [italic]/nick <new_username>[/]."
        SELF_CONNECTED = "Connected to server."
        OTHER_CONNECTED = "{} has connected to the server."
        SELF_DISCONNECTED = "Disconnected from server."
        OTHER_DISCONNECTED = "{} has disconnected from the server."
        USERNAME_CHANGE = "{}'s username has been changed to {}."
