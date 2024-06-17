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
        if type_ not in self._expected_types:
            raise ValueError(f"Invalid type: {type_}")
        self._handlers[type_].append(subscriber)

    def unsubscribe(self, type_: str, subscriber: Callable):
        if type_ not in self._expected_types:
            raise ValueError(f"Invalid type: {type_}")
        self._handlers[type_].remove(subscriber)

    def notify(self, type_: str, *args, **kwargs):
        if type_ not in self._expected_types:
            raise ValueError(f"Invalid type: {type_}")
        for subscriber in self._handlers[type_]:
            subscriber(*args, **kwargs)

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def send_message(self, message: str):
        raise NotImplementedError

    def update_username(self, new_username: str):
        raise NotImplementedError


class ServerHandler(GenericHandler):
    """Handler for server (centralized) connections"""

    # noinspection t
    def __init__(self, server_address: str):
        """Create a new ServerHandler instance

        :param server_address: The address of the server to connect to
        """
        super().__init__()

        self.sock = socketio.Client()
        self.server_address = server_address

        @self.sock.event
        def connect():
            pass  # TODO

        @self.sock.event
        def connect_response(data: dict):
            flags = data.get("flags", [])
            if data.get("success", False):
                self.notify("display_system", Strings.SELF_CONNECTED_TO_SERVER)
                if "motd" in data and data["motd"] is not None:
                    self.notify("display_motd", data["motd"])

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
                self.sock.disconnect()
                if "version_missing" in flags:
                    raise ValueError("Client version missing")  # should not happen

        @self.sock.event
        def connect_broadcast(data: dict):
            self.notify(
                "display_event",
                Strings.OTHER_CONNECTED_TO_SERVER.format(
                    data.get("username", "UNKNOWN")
                ),
            )

        @self.sock.event
        def disconnect():
            pass  # TODO

        @self.sock.event
        def disconnect_broadcast(data: dict):
            self.notify(
                "display_event",
                Strings.OTHER_DISCONNECTED_FROM_SERVER.format(
                    data.get("username", "UNKNOWN")
                ),
            )

        @self.sock.event
        def message_broadcast(data: dict):
            self.notify(
                "display_message",
                data.get("sender", "UNKNOWN"),
                data.get("message", "UNKNOWN"),
            )

        @self.sock.event
        def username_update_broadcast(data: dict):
            self.notify(
                "display_event",
                Strings.USERNAME_CHANGE.format(
                    data.get("old", "UNKNOWN"), data.get("new", "UNKNOWN")
                ),
            )

        @self.sock.event
        def global_error(data: dict):
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
