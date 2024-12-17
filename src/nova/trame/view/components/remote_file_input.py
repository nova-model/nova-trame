"""View implementation for RemoteFileInput."""

from functools import partial
from typing import Any, Optional, Union, cast

from trame.app import get_server
from trame.widgets import client, html
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets.core import AbstractElement

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.model.remote_file_input import RemoteFileInputModel
from nova.trame.view.components import InputField
from nova.trame.view_model.remote_file_input import RemoteFileInputViewModel


class RemoteFileInput:
    """Generates a file selection dialog for picking files off of the server.

    You cannot use typical Trame :code:`with` syntax to add children to this.
    """

    def __init__(
        self,
        v_model: Optional[Union[tuple[str, Any], str]] = None,
        allow_files: bool = True,
        allow_folders: bool = False,
        allow_nonexistent_path: bool = False,
        base_paths: Optional[list[str]] = None,
        dialog_props: Optional[dict[str, Any]] = None,
        extensions: Optional[list[str]] = None,
        input_props: Optional[dict[str, Any]] = None,
    ) -> None:
        """Constructor for RemoteFileInput.

        Parameters
        ----------
        v_model : tuple[str, Any] or str, optional
            The v-model for this component. If this references a Pydantic configuration variable, then this component
            will attempt to load a label, hint, and validation rules from the configuration for you automatically.
        allow_files : bool
            If true, the user can save a file selection.
        allow_folders : bool
            If true, the user can save a folder selection.
        allow_nonexistent_path : bool
            If false, the user will be warned when they've selected a non-existent path on the filesystem.
        base_paths : list[str], optional
            Only files under these paths will be shown.
        dialog_props : dict[str, typing.Any], optional
            Props to be passed to VDialog.
        extensions : list[str], optional
            Only files with these extensions will be shown by default. The user can still choose to view all files.
        input_props : dict[str, typing.Any], optional
            Props to be passed to InputField.

        Raises
        ------
        ValueError
            If v_model is None.

        Returns
        -------
        None
        """
        if v_model is None:
            raise ValueError("RemoteFileInput must have a v_model attribute.")

        self.v_model = v_model
        self.allow_files = allow_files
        self.allow_folders = allow_folders
        self.allow_nonexistent_path = allow_nonexistent_path
        self.base_paths = base_paths if base_paths else ["/"]
        self.dialog_props = dict(dialog_props) if dialog_props else {}
        self.extensions = extensions if extensions else []
        self.input_props = dict(input_props) if input_props else {}

        if "__events" not in self.input_props:
            self.input_props["__events"] = []
        self.input_props["__events"].append("change")

        if "width" not in self.dialog_props:
            self.dialog_props["width"] = 600

        self.create_model()
        self.create_viewmodel()
        self.create_ui()

    def create_ui(self) -> None:
        with cast(
            AbstractElement,
            InputField(
                v_model=self.v_model,
                change=(self.vm.select_file, "[$event.target.value]"),
                **self.input_props,
            ),
        ) as input:
            self.vm.init_view()

            with vuetify.Template(v_slot_append=True):
                with vuetify.VBtn(icon=True, size="small", click=self.vm.open_dialog):
                    vuetify.VIcon("mdi-folder-open")

                    with vuetify.VDialog(
                        v_model=self.vm.get_dialog_state_name(), activator="parent", **self.dialog_props
                    ):
                        with vuetify.VCard(classes="pa-4"):
                            vuetify.VCardTitle(input.label)
                            vuetify.VTextField(
                                v_model=self.vm.get_filter_state_name(),
                                classes="mb-4 px-4",
                                label="Current Selection",
                                __events=["change"],
                                change=(self.vm.select_file, "[$event.target.value]"),
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

    def create_model(self) -> None:
        self.model = RemoteFileInputModel(self.allow_files, self.allow_folders, self.base_paths, self.extensions)

    def create_viewmodel(self) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)

        if isinstance(self.v_model, tuple):
            model_name = self.v_model[0]
        else:
            model_name = self.v_model

        self.vm = RemoteFileInputViewModel(self.model, binding)

        self.vm.dialog_bind.connect(self.vm.get_dialog_state_name())
        self.vm.file_list_bind.connect(self.vm.get_file_list_state_name())
        self.vm.filter_bind.connect(self.vm.get_filter_state_name())
        self.vm.on_close_bind.connect(client.JSEval(exec=f"{self.vm.get_dialog_state_name()} = false;").exec)
        self.vm.on_update_bind.connect(
            client.JSEval(exec=f"{model_name} = $event; flushState('{model_name.split('.')[0].split('[')[0]}');").exec
        )
        self.vm.showing_all_bind.connect(self.vm.get_showing_all_state_name())
        self.vm.valid_selection_bind.connect(self.vm.get_valid_selection_state_name())
