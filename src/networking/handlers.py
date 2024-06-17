from collections import defaultdict
from typing import Callable

import socketio

from gvars import *


class GenericHandler:
    """Generic handler for connections - should not be used directly"""

    def __init__(self):
        self._handlers = defaultdict(list)
        self._expected_types = (
            "display_message",
            "display_motd",
            "display_event",
            "display_server",
            "display_system",
            "display_error",
            "handle_error",
            "handle_fatal_error",
        )

    def subscribe(self, type_: str, subscriber: Callable):
        """Subscribe to a specific event type. Event should be one of the expected types."""
        if type_ not in self._expected_types:
            raise ValueError(f"Invalid type: {type_}")
        self._handlers[type_].append(subscriber)

    def unsubscribe(self, type_: str, subscriber: Callable):
        """Unsubscribe from a specific event type. Event should be one of the expected types."""
        if type_ not in self._expected_types:
            raise ValueError(f"Invalid type: {type_}")
        self._handlers[type_].remove(subscriber)

    def notify(self, type_: str, *args, **kwargs):
        """Notify all subscribers of a specific event type. Event should be one of the expected types."""
        if type_ not in self._expected_types:
            raise ValueError(f"Invalid type: {type_}")
        for subscriber in self._handlers[type_]:
            subscriber(*args, **kwargs)

    def connect(self, username: str = None):
        """Connect to the [P2P] server with the given username.

        :param username: The username to connect with, or None for server-assigned
        """
        raise NotImplementedError

    def disconnect(self):
        """Disconnect from the [P2P] server."""
        raise NotImplementedError

    def send_message(self, message: str):
        """Send a message to the [P2P] server.

        :param message: The message to send
        """
        raise NotImplementedError

    def update_username(self, new_username: str):
        """Request a username change to the [P2P] server.

        :param new_username: The new username to request
        """
        raise NotImplementedError


class ServerHandler(GenericHandler):
    """Handler for server (centralized) connections"""

    # noinspection t
    def __init__(self, server_address: str):
        """Create a new ServerHandler instance

        :param server_address: The address of the server to connect to
        """
        super().__init__()

        # Create a new socket.io client
        self.sock = socketio.Client()
        self.server_address = server_address

        # Register socket.io event handlers
        @self.sock.event
        def connect():
            """Called upon the initial connection to the server."""
            pass  # TODO

        @self.sock.event
        def connect_response(data: dict):
            """Emitted by the server in response to a connection attempt.

            :param data: The data sent by the server, expected:
                | success: Whether the connection was successful
                | motd: The message of the day
                | flags: Any flags that were set
                | username: The username that was assigned to the client
            """
            flags = data.get(
                "flags", []
            )  # flags are used to indicate special conditions
            if data.get(
                "success", False
            ):  # if the connection was successful, default to False
                # Notify that we've connected to the server
                self.notify("display_system", Strings.SELF_CONNECTED_TO_SERVER)

                # Display the MOTD
                if "motd" in data and data["motd"] is not None:
                    self.notify("display_motd", data["motd"])

                # Handle username-related flags
                if "username_missing" in flags:
                    self.notify(
                        "display_system",
                        Strings.USERNAME_MISSING.format(
                            data.get("username", "UNKNOWN")
                        ),
                    )
                elif "username_taken" in flags:
                    self.notify(
                        "display_system",
                        Strings.USERNAME_TAKEN.format(data.get("username", "UNKNOWN")),
                    )
            else:
                self.sock.disconnect()  # disconnect from the server, to combat pesky ghost connections
                if "version_missing" in flags:
                    raise ValueError("Client version missing")  # should not happen

        @self.sock.event
        def connect_broadcast(data: dict):
            """Emitted by the server when a new user connects.

            :param data: The data sent by the server, expected:
                | username: The username of the user that connected
            """
            self.notify(
                "display_event",
                Strings.OTHER_CONNECTED_TO_SERVER.format(
                    data.get("username", "UNKNOWN")
                ),
            )

        @self.sock.event
        def disconnect():
            """Called upon disconnection from the server."""
            pass  # TODO

        @self.sock.event
        def disconnect_broadcast(data: dict):
            """Emitted by the server when a user disconnects.

            :param data: The data sent by the server, expected:
                | username: The username of the user that disconnected
            """
            self.notify(
                "display_event",
                Strings.OTHER_DISCONNECTED_FROM_SERVER.format(
                    data.get("username", "UNKNOWN")
                ),
            )

        @self.sock.event
        def message_broadcast(data: dict):
            """Emitted by the server when a user sends a message (including self).

            :param data: The data sent by the server, expected:
                | sender: The username of the user that sent the message
                | message: The message that was sent
            """
            self.notify(
                "display_message",
                data.get("sender", "UNKNOWN"),
                data.get("message", "UNKNOWN"),
            )

        @self.sock.event
        def username_update_broadcast(data: dict):
            """Emitted by the server when a user changes their username (including self).

            :param data: The data sent by the server, expected:
                | old: The old username
                | new: The new username
            """
            self.notify(
                "display_event",
                Strings.USERNAME_CHANGE.format(
                    data.get("old", "UNKNOWN"), data.get("new", "UNKNOWN")
                ),
            )

        @self.sock.event
        def global_error(data: dict):
            """Emitted by the server when any global (misc.) error occurs.

            :param data: The data sent by the server, expected:
                | fatal: Whether the error is fatal
                | type: The type of the error
                | message: The error message
            """
            if data.get("fatal", False):
                if "message" in data and data["message"] is not None:
                    self.notify("display_error", data["message"])
                self.notify("handle_fatal_error", data.get("type", "UNKNOWN"))
                self.sock.disconnect()
            else:
                if "message" in data and data["message"] is not None:
                    self.notify("display_error", data["message"])
                self.notify("handle_error", data.get("type", "UNKNOWN"))

    def connect(self, username: str = None):
        self.sock.connect(
            self.server_address,
            headers={"client-version": VERSION, "username": username},
        )

    def disconnect(self):
        self.sock.disconnect()

    def send_message(self, message: str):
        self.sock.emit("message", {"message": message})

    def update_username(self, new_username: str):
        self.sock.emit("username_update", new_username)


class P2PHandler(GenericHandler):
    """Handler for P2P connections"""
