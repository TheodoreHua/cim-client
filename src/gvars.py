VERSION = "0.0.1"  # The version of the client


class Strings:
    """Global strings for the application."""

    # UI
    TITLE = f"CIM Chat (v{VERSION})"
    TEXT_BAR_PLACEHOLDER = "Type your message here..."

    # SERVER COMMUNICATION
    USERNAME_MISSING = "You did not provide a username. You have been assigned [italic]{}[/] as your temporary username. You can change it with [italic]/nick <new_username>[/]."
    USERNAME_TAKEN = "Your username was [underline]already taken[/underline. You have been assigned [italic]{}[/] as your temporary username. You can change it with [italic]/nick <new_username>[/]."
    SELF_CONNECTED_TO_SERVER = "Connected to server."
    OTHER_CONNECTED_TO_SERVER = "{} has connected to the server."
    SELF_DISCONNECTED_FROM_SERVER = "Disconnected from server."
    OTHER_DISCONNECTED_FROM_SERVER = "{} has disconnected from the server."
    USERNAME_CHANGE = "{}'s username has been changed to {}."
