"""Entrypoint for the widget gallery."""

import sys
from typing import Any

from trame_server.core import Server

from tests.gallery import App


def main(server: Server = None, **kwargs: Any) -> None:
    # [run app]
    app = App(server)
    for arg in sys.argv[1:]:
        try:
            key, value = arg.split("=")
            kwargs[key] = int(value)
        except Exception:
            pass
    app.server.start(**kwargs)
    # [run app complete]
