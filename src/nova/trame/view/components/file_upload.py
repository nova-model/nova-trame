"""View implementation for FileUpload."""

from typing import Any, List, Optional

from trame.widgets import vuetify3 as vuetify

from .remote_file_input import RemoteFileInput


class FileUpload(vuetify.VBtn):
    """Component for uploading a file from either the user's filesystem or the server filesystem."""

    def __init__(self, v_model: str, base_paths: Optional[List[str]] = None, label: str = "", **kwargs: Any) -> None:
        """Constructor for FileUpload.

        Parameters
        ----------
        v_model : str
            The state variable to set when the user uploads their file. The state variable will contain a latin1-decoded
            version of the file contents. If your file is binary or requires a different string encoding, then you can
            call `encode('latin1')` on the file contents to get the underlying bytes.
        base_paths: list[str], optional
            Passed to :ref:`RemoteFileInput <api_remotefileinput>`.
        label : str, optional
            The text to display on the upload button.
        **kwargs
            All other arguments will be passed to the underlying
            `Button component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VBtn>`_.

        Returns
        -------
        None
        """
        self._v_model = v_model
        if base_paths:
            self._base_paths = base_paths
        else:
            self._base_paths = ["/"]
        self._ref_name = f"nova__fileupload_{self._next_id}"

        super().__init__(label, **kwargs)
        self.create_ui()

    def create_ui(self) -> None:
        self.local_file_input = vuetify.VFileInput(
            v_model=(self._v_model, None),
            classes="d-none",
            ref=self._ref_name,
            # Serialize the content in a way that will work with nova-mvvm and then push it to the server.
            update_modelValue=(
                f"{self._v_model}.arrayBuffer().then((contents) => {{"
                f"trigger('decode_blob_{self._id}', [contents]); "
                "});"
            ),
        )
        self.remote_file_input = RemoteFileInput(
            v_model=self._v_model, base_paths=self._base_paths, input_props={"classes": "d-none"}, return_contents=True
        )

        with self:
            with vuetify.VMenu(activator="parent"):
                with vuetify.VList():
                    vuetify.VListItem("From Local Machine", click=f"trame.refs.{self._ref_name}.click()")
                    vuetify.VListItem("From Analysis Cluster", click=self.remote_file_input.open_dialog)

        @self.server.controller.trigger(f"decode_blob_{self._id}")
        def _decode_blob(contents: bytes) -> None:
            self.remote_file_input.decode_file(contents)

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
