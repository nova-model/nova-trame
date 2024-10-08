"""Implementation of LocalStorageManager."""

from asyncio import sleep
from typing import Any, Optional

from trame.widgets import client
from trame_server.core import Controller


class LocalStorageManager:
    """Allows manipulation of window.localStorage from your Python code.

    LocalStorageManager requires a Trame layout to exist in order to work properly. Because of this, it's strongly
    recommended that you don't use this class directly. Instead, ThemedApp automatically creates an instance of this
    class and stores it in ThemedApp.local_storage, through which it can safely be used.
    """

    def __init__(self, ctrl: Controller) -> None:
        """Constructor for the LocalStorageManager class.

        Parameters
        ----------
        ctrl : `trame_server.core.Controller <https://trame.readthedocs.io/en/latest/core.controller.html#trame_server.controller.Controller>`_
            The Trame controller.

        Returns
        -------
        None
        """
        self.js_get = client.JSEval(
            exec=(
                "window.trame.trigger("
                "  'facade__local_storage_trigger', "
                "  [$event.key, window.localStorage.getItem($event.key)]"
                ");"
            )
        ).exec
        self.js_remove = client.JSEval(exec="window.localStorage.removeItem($event.key);").exec
        self.js_set = client.JSEval(exec="window.localStorage.setItem($event.key, $event.value);").exec

        self._ready: dict[str, bool] = {}
        self._values: dict[str, str] = {}

        @ctrl.trigger("facade__local_storage_trigger")
        def _(key: str, value: str) -> None:
            self._ready[key] = True
            self._values[key] = value

    async def get(self, key: str) -> Optional[str]:
        """Gets the value of a key from window.localStorage.

        You cannot call this from the main Trame coroutine because this waits on a response from the browser that must
        be processed by the main coroutine. Instead, you should call this from another thread or coroutine, typically
        with :code:`asyncio.create_task`.

        Parameters
        ----------
        key : str
            The key to get the value of.

        Returns
        -------
        Optional[str]
            The value of the key from window.localStorage.
        """
        self._ready[key] = False
        self.js_get({"key": key})

        while not self._ready[key]:
            await sleep(0.1)

        return self._values[key]

    def remove(self, key: str) -> None:
        """Removes a key from window.localStorage.

        Parameters
        ----------
        key : str
            The key to remove.

        Returns
        -------
        None
        """
        self.js_remove({"key": key})

    def set(self, key: str, value: Any) -> None:
        """Sets the value of a key in window.localStorage.

        Parameters
        ----------
        key : str
            The key to set the value of.
        value : typing.Any
            The value to set. This value will be coerced to a string before being stored.

        Returns
        -------
        None
        """
        self.js_set({"key": key, "value": value})
