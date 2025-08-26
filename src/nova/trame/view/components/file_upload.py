"""View implementation for FileUpload."""

from typing import Any, List, Tuple, Union

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify
from trame_server.core import State

from nova.trame._internal.utils import get_state_param

from .remote_file_input import RemoteFileInput


class FileUpload(vuetify.VBtn):
    """Component for uploading a file from either the user's filesystem or the server filesystem."""

    def __init__(
        self,
        v_model: Union[str, Tuple],
        base_paths: Union[List[str], Tuple, None] = None,
        extensions: Union[List[str], Tuple, None] = None,
        label: str = "",
        return_contents: Union[bool, Tuple] = True,
        use_bytes: Union[bool, Tuple] = False,
        **kwargs: Any,
    ) -> None:
        """Constructor for FileUpload.

        Parameters
        ----------
        v_model : Union[str, Tuple]
            The state variable to set when the user uploads their file. The state variable will contain a latin1-decoded
            version of the file contents. If your file is binary or requires a different string encoding, then you can
            call `encode('latin1')` on the file contents to get the underlying bytes.
        base_paths: Union[List[str], Tuple], optional
            Passed to :ref:`RemoteFileInput <api_remotefileinput>`.
        extensions: Union[List[str], Tuple], optional
            Restricts the files shown to the user to files that end with one of the strings in the list.
        label : str, optional
            The text to display on the upload button.
        return_contents : Union[bool, Tuple], optional
            If true, the file contents will be stored in v_model. If false, a file path will be stored in v_model.
            Defaults to true.
        use_bytes : Union[bool, Tuple], optional
            If true, then files uploaded from the local machine will contain bytes rather than text.
        **kwargs
            All other arguments will be passed to the underlying
            `Button component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VBtn>`_.

        Returns
        -------
        None
        """
        self._server = get_server(None, client_type="vue3")

        self._v_model = v_model
        self._base_paths = base_paths if base_paths else ["/"]
        self._extensions = extensions if extensions else []
        self._return_contents = return_contents
        self._use_bytes = use_bytes
        self._ref_name = f"nova__fileupload_{self._next_id}"

        super().__init__(label, **kwargs)
        self.create_ui()

    @property
    def state(self) -> State:
        return self._server.state

    def create_ui(self) -> None:
        self.local_file_input = vuetify.VFileInput(
            v_model=self._v_model,
            __properties=["accept"],
            accept=",".join(self._extensions) if isinstance(self._extensions, list) else self._extensions,
            classes="d-none",
            ref=self._ref_name,
            # Serialize the content in a way that will work with nova-mvvm and then push it to the server.
            update_modelValue=(
                f"{self._v_model}.arrayBuffer().then((contents) => {{"
                f"  trigger('decode_blob_{self._id}', [contents]); "
                "});"
            ),
        )
        self.remote_file_input = RemoteFileInput(
            v_model=self._v_model,
            base_paths=self._base_paths,
            extensions=self._extensions,
            input_props={"classes": "d-none"},
            return_contents=self._return_contents,
            use_bytes=self._use_bytes,
        )

        with self:
            with vuetify.VMenu(activator="parent"):
                with vuetify.VList():
                    vuetify.VListItem("From Local Machine", click=f"trame.refs.{self._ref_name}.click()")
                    vuetify.VListItem("From Analysis Cluster", click=self.remote_file_input.open_dialog)

        @self.server.controller.trigger(f"decode_blob_{self._id}")
        def _decode_blob(contents: bytes) -> None:
            self.remote_file_input.decode_file(contents, get_state_param(self.state, self._return_contents))

    def select_file(self, value: str) -> None:
        """Programmatically set the RemoteFileInput path.

        Parameters
        ----------
        value: str
            The new value for the RemoteFileInput.

        Returns
        -------
        None
        """
        self.remote_file_input.select_file(value)
