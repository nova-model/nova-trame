"""View implementation for RemoteFileInput."""

from functools import partial
from tempfile import NamedTemporaryFile
from typing import Any, List, Optional, Tuple, Union, cast

from trame.app import get_server
from trame.widgets import client, html
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets.core import AbstractElement
from trame_server.core import State

from nova.mvvm._internal.utils import rgetdictvalue
from nova.mvvm.trame_binding import TrameBinding
from nova.trame._internal.utils import get_state_name, get_state_param, set_state_param
from nova.trame.model.remote_file_input import RemoteFileInputModel
from nova.trame.view_model.remote_file_input import RemoteFileInputViewModel

from .input_field import InputField


class RemoteFileInput:
    """Generates a file selection dialog for picking files off of the server.

    You cannot use typical Trame :code:`with` syntax to add children to this.
    """

    def __init__(
        self,
        v_model: Union[str, Tuple],
        allow_files: Union[bool, Tuple] = True,
        allow_folders: Union[bool, Tuple] = False,
        base_paths: Union[List[str], Tuple, None] = None,
        dialog_props: Optional[dict[str, Any]] = None,
        extensions: Union[List[str], Tuple, None] = None,
        input_props: Optional[dict[str, Any]] = None,
        return_contents: Union[bool, Tuple] = False,
        use_bytes: Union[bool, Tuple] = False,
    ) -> None:
        """Constructor for RemoteFileInput.

        Parameters
        ----------
        v_model : Union[str, Tuple]
            The v-model for this component. If this references a Pydantic configuration variable, then this component
            will attempt to load a label, hint, and validation rules from the configuration for you automatically.
        allow_files : Union[bool, Tuple], optional
            If true, the user can save a file selection.
        allow_folders : Union[bool, Tuple], optional
            If true, the user can save a folder selection.
        base_paths : Union[List[str], Tuple], optional
            Only files under these paths will be shown.
        dialog_props : Dict[str, typing.Any], optional
            Props to be passed to VDialog.
        extensions : Union[List[str], Tuple], optional
            Only files with these extensions will be shown by default. The user can still choose to view all files.
        input_props : Dict[str, typing.Any], optional
            Props to be passed to InputField.
        return_contents : Union[bool, Tuple], optional
            If true, then the v_model will contain the contents of the file. If false, then the v_model will contain the
            path of the file. Defaults to false.
        use_bytes : Union[bool, Tuple], optional
            If true, then the file contents will be treated as bytestreams when calling decode_file.

        Returns
        -------
        None
        """
        self.server = get_server(None, client_type="vue3")

        self.v_model = v_model
        self.allow_files = allow_files
        self.allow_folders = allow_folders
        self.base_paths = base_paths if base_paths else ["/"]
        self.dialog_props = dict(dialog_props) if dialog_props else {}
        self.extensions = extensions if extensions else []
        self.input_props = dict(input_props) if input_props else {}
        self.return_contents = return_contents
        self.use_bytes = use_bytes

        if "__events" not in self.input_props:
            self.input_props["__events"] = []
        self.input_props["__events"].append("change")

        if "width" not in self.dialog_props:
            self.dialog_props["width"] = 600

        self._create_model()
        self._create_viewmodel()
        self._setup_bindings()

        self.create_ui()

    @property
    def state(self) -> State:
        return self.server.state

    def create_ui(self) -> None:
        with cast(
            AbstractElement,
            InputField(
                v_model=self.v_model,
                change=(self.vm.select_file, "[$event.target.value]"),
                **self.input_props,
            ),
        ) as input:
            if isinstance(input.classes, str):
                input.classes += " nova-remote-file-input"
            else:
                input.classes = "nova-remote-file-input"
            self.vm.init_view()

            with vuetify.Template(v_slot_append=True):
                with vuetify.VBtn(icon=True, size="small", click=self.vm.open_dialog):
                    vuetify.VIcon("mdi-folder-open")

                    with vuetify.VDialog(
                        v_model=self.vm.get_dialog_state_name(), activator="parent", **self.dialog_props
                    ):
                        with vuetify.VCard(classes="pa-4"):
                            vuetify.VTextField(
                                v_model=self.vm.get_filter_state_name(),
                                classes="mb-4 px-4",
                                label=input.label,
                                variant="outlined",
                                update_modelValue=(self.vm.filter_paths, "[$event]"),
                            )

                            if self.allow_files and self.extensions:
                                with html.Div(v_if=(f"{self.vm.get_showing_all_state_name()}",)):
                                    vuetify.VListSubheader("All Available Files")
                                    vuetify.VBtn(
                                        "Don't show all",
                                        classes="mb-4",
                                        size="small",
                                        click=self.vm.toggle_showing_all_files,
                                    )
                                with html.Div(v_else=True):
                                    vuetify.VListSubheader(
                                        f"Available Files with Extensions: {', '.join(self.extensions)}"
                                    )
                                    vuetify.VBtn(
                                        "Show all",
                                        classes="mb-4",
                                        size="small",
                                        click=self.vm.toggle_showing_all_files,
                                    )
                            elif self.allow_files:
                                vuetify.VListSubheader("Available Files")
                            else:
                                vuetify.VListSubheader("Available Folders")

                            with vuetify.VList(classes="mb-4"):
                                self.vm.populate_file_list()

                                vuetify.VListItem(
                                    "{{ file.path }}",
                                    v_for=f"file, index in {self.vm.get_file_list_state_name()}",
                                    classes=(
                                        f"index < {self.vm.get_file_list_state_name()}.length - 1 "
                                        "? 'border-b-thin' "
                                        ": ''",
                                    ),
                                    prepend_icon=("file.directory ? 'mdi-folder' : 'mdi-file'",),
                                    click=(self.vm.select_file, "[file]"),
                                )

                            with html.Div(classes="text-center"):
                                vuetify.VBtn(
                                    "OK",
                                    classes="mr-4",
                                    disabled=(f"!{self.vm.get_valid_selection_state_name()}",),
                                    click=self.vm.close_dialog,
                                )
                                vuetify.VBtn(
                                    "Cancel",
                                    color="lightgrey",
                                    click=partial(self.vm.close_dialog, cancel=True),
                                )

    def _create_model(self) -> None:
        self.model = RemoteFileInputModel()

    def _create_viewmodel(self) -> None:
        binding = TrameBinding(self.state)

        if isinstance(self.v_model, tuple):
            model_name = self.v_model[0]
        else:
            model_name = self.v_model

        self.set_v_model = client.JSEval(
            exec=f"{model_name} = $event; flushState('{model_name.split('.')[0].split('[')[0]}');"
        ).exec

        self.vm = RemoteFileInputViewModel(self.model, binding)

        self.vm.dialog_bind.connect(self.vm.get_dialog_state_name())
        self.vm.file_list_bind.connect(self.vm.get_file_list_state_name())
        self.vm.filter_bind.connect(self.vm.get_filter_state_name())
        self.vm.on_close_bind.connect(client.JSEval(exec=f"{self.vm.get_dialog_state_name()} = false;").exec)
        self.vm.showing_all_bind.connect(self.vm.get_showing_all_state_name())
        self.vm.valid_selection_bind.connect(self.vm.get_valid_selection_state_name())

    # This method sets up Trame state change listeners for each binding parameter that can be changed directly by this
    # component. This allows us to communicate the changes to the developer's bindings without requiring our own. We
    # don't want bindings in the internal implementation as our callbacks could compete with the developer's.
    def _setup_bindings(self) -> None:
        # If the bindings were given initial values, write these to the state.
        self._last_allow_files = set_state_param(self.state, self.allow_files)
        self._last_allow_folders = set_state_param(self.state, self.allow_folders)
        self._last_base_paths = set_state_param(self.state, self.base_paths)
        self._last_extensions = set_state_param(self.state, self.extensions)
        self._last_return_contents = set_state_param(self.state, self.return_contents)

        # Now we need to propagate the state to this component's view model.
        self.vm.set_binding_parameters(
            allow_files=self.allow_files,
            allow_folders=self.allow_folders,
            base_paths=self.base_paths,
            extensions=self.extensions,
        )
        self._setup_update_binding(self._last_return_contents)

        # Now we set up the change listeners for all bound parameters. These are responsible for updating the component
        # when other portions of the application manipulate these parameters.
        if isinstance(self.allow_files, tuple):

            @self.state.change(get_state_name(self.allow_files[0]))
            def on_allow_files_change(**kwargs: Any) -> None:
                if isinstance(self.allow_files, bool):
                    return
                allow_files = rgetdictvalue(kwargs, self.allow_files[0])
                if allow_files != self._last_allow_files:
                    self.vm.set_binding_parameters(
                        allow_files=set_state_param(self.state, self.allow_files, allow_files)
                    )

        if isinstance(self.allow_folders, tuple):

            @self.state.change(get_state_name(self.allow_folders[0]))
            def on_allow_folders_change(**kwargs: Any) -> None:
                if isinstance(self.allow_folders, bool):
                    return
                allow_folders = rgetdictvalue(kwargs, self.allow_folders[0])
                if allow_folders != self._last_allow_folders:
                    self.vm.set_binding_parameters(
                        allow_folders=set_state_param(self.state, self.allow_folders, allow_folders)
                    )

        if isinstance(self.base_paths, tuple):

            @self.state.change(get_state_name(self.base_paths[0]))
            def on_base_paths_change(**kwargs: Any) -> None:
                if isinstance(self.base_paths, bool):
                    return
                base_paths = rgetdictvalue(kwargs, self.base_paths[0])
                if base_paths != self._last_base_paths:
                    self.vm.set_binding_parameters(base_paths=set_state_param(self.state, self.base_paths, base_paths))

        if isinstance(self.extensions, tuple):

            @self.state.change(get_state_name(self.extensions[0]))
            def on_extensions_change(**kwargs: Any) -> None:
                if isinstance(self.extensions, bool):
                    return
                extensions = rgetdictvalue(kwargs, self.extensions[0])
                if extensions != self._last_extensions:
                    self.vm.set_binding_parameters(extensions=set_state_param(self.state, self.extensions, extensions))

        if isinstance(self.return_contents, tuple):

            @self.state.change(get_state_name(self.return_contents[0]))
            def on_return_contents_change(**kwargs: Any) -> None:
                if isinstance(self.return_contents, bool):
                    return
                return_contents = rgetdictvalue(kwargs, self.return_contents[0])
                if return_contents != self._last_return_contents:
                    self._setup_update_binding(return_contents)

    def _setup_update_binding(self, read_file: bool) -> None:
        self.vm.reset_update_binding()
        if read_file:
            self.vm.on_update_bind.connect(self.read_file)
        else:
            self.vm.on_update_bind.connect(self.set_v_model)

    def read_file(self, file_path: str) -> None:
        with open(file_path, mode="rb") as file:
            self.decode_file(file.read())

    def decode_file(self, bytestream: bytes, set_contents: bool = False) -> None:
        use_bytes = get_state_param(self.state, self.use_bytes)

        decoded_content = bytestream.decode("latin1")
        if set_contents:
            self.set_v_model(decoded_content)
        else:
            if use_bytes:
                with NamedTemporaryFile(mode="wb", delete=False) as temp_file:
                    temp_file.write(bytestream)
                    temp_file.flush()
                    self.set_v_model(temp_file.name)
            else:
                with NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
                    temp_file.write(decoded_content)
                    temp_file.flush()
                    self.set_v_model(temp_file.name)

    def select_file(self, value: str) -> None:
        """Programmatically set the v_model value."""
        self.vm.select_file(value)

    def open_dialog(self) -> None:
        """Programmatically opens the dialog for selecting a file."""
        self.vm.open_dialog()
