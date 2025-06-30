"""View Implementation for DataSelector."""

from asyncio import ensure_future, sleep
from typing import Any, List, Optional, cast

from trame.app import get_server
from trame.widgets import client, datagrid, html
from trame.widgets import vuetify3 as vuetify

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.model.data_selector import DataSelectorModel, DataSelectorState
from nova.trame.view.layouts import GridLayout, HBoxLayout, VBoxLayout
from nova.trame.view_model.data_selector import DataSelectorViewModel

from .input_field import InputField

vuetify.enable_lab()


class DataSelector(datagrid.VGrid):
    """Allows the user to select datafiles from the server."""

    def __init__(
        self,
        v_model: str,
        directory: str,
        extensions: Optional[List[str]] = None,
        prefix: str = "",
        refresh_rate: int = 30,
        select_strategy: str = "all",
        **kwargs: Any,
    ) -> None:
        """Constructor for DataSelector.

        Parameters
        ----------
        v_model : str
            The name of the state variable to bind to this widget. The state variable will contain a list of the files
            selected by the user.
        directory : str
            The top-level folder to expose to users. Only contents of this directory and its children will be exposed to
            users.
        extensions : List[str], optional
            A list of file extensions to restrict selection to. If unset, then all files will be shown.
        prefix : str, optional
            A subdirectory within the selected top-level folder to show files. If not specified, the user will be shown
            a folder browser and will be able to see all files in the selected top-level folder.
        refresh_rate : int, optional
            The number of seconds between attempts to automatically refresh the file list. Set to zero to disable this
            feature. Defaults to 30 seconds.
        select_strategy : str, optional
            The selection strategy to pass to the `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`__.
            If unset, the `all` strategy will be used.
        **kwargs
            All other arguments will be passed to the underlying
            `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`_.

        Returns
        -------
        None
        """
        if "allow_custom_directory" in kwargs or "facility" in kwargs or "instrument" in kwargs:
            raise TypeError(
                "The old DataSelector component has been renamed to NeutronDataSelector. Please import it from "
                "`nova.trame.view.components.ornl`."
            )

        if "items" in kwargs:
            raise AttributeError("The items parameter is not allowed on DataSelector widget.")

        if "label" in kwargs:
            self._label = kwargs["label"]
        else:
            self._label = None

        self._v_model = v_model
        self._v_model_name_in_state = v_model.split(".")[0]
        self._directory = directory
        self._extensions = extensions if extensions is not None else []
        self._prefix = prefix
        self._refresh_rate = refresh_rate
        self._select_strategy = select_strategy

        self._revogrid_id = f"nova__dataselector_{self._next_id}_rv"
        self._state_name = f"nova__dataselector_{self._next_id}_state"
        self._directories_name = f"nova__dataselector_{self._next_id}_directories"
        self._datafiles_name = f"nova__dataselector_{self._next_id}_datafiles"

        self._flush_state = f"flushState('{self._v_model_name_in_state}');"
        self._reset_rv_grid = client.JSEval(
            exec=f"window.grid_manager.get('{self._revogrid_id}').updateCheckboxes()"
        ).exec
        self._reset_state = client.JSEval(exec=f"{self._v_model} = []; {self._flush_state}").exec

        self.create_model()
        self.create_viewmodel()

        self.create_ui(**kwargs)

        ensure_future(self._refresh_loop())

    def create_ui(self, *args: Any, **kwargs: Any) -> None:
        with VBoxLayout(classes="nova-data-selector", height="100%") as self._layout:
            with HBoxLayout(valign="center"):
                self._layout.filter = html.Div(classes="flex-1-1")
                with vuetify.VBtn(
                    classes="mx-1", density="compact", icon=True, variant="text", click=self.refresh_contents
                ):
                    vuetify.VIcon("mdi-refresh")
                    vuetify.VTooltip("Refresh Contents", activator="parent")

            with GridLayout(columns=2, classes="flex-1-0 h-0", valign="start"):
                if not self._prefix:
                    with html.Div(classes="d-flex flex-column h-100 overflow-hidden"):
                        vuetify.VListSubheader("Available Directories", classes="flex-0-1 justify-center px-0")
                        vuetify.VTreeview(
                            v_if=(f"{self._directories_name}.length > 0",),
                            activatable=True,
                            active_strategy="single-independent",
                            classes="flex-1-0 h-0 overflow-y-auto",
                            fluid=True,
                            item_value="path",
                            items=(self._directories_name,),
                            click_open=(self._vm.expand_directory, "[$event.path]"),
                            update_activated=(self._vm.set_subdirectory, "$event"),
                        )
                        vuetify.VListItem("No directories found", classes="flex-0-1 text-center", v_else=True)

                super().__init__(
                    v_model=self._v_model,
                    can_focus=False,
                    columns=(
                        "[{"
                        "    cellTemplate: (createElement, props) =>"
                        f"       window.grid_manager.get('{self._revogrid_id}').cellTemplate(createElement, props),"
                        "    columnTemplate: (createElement) =>"
                        f"       window.grid_manager.get('{self._revogrid_id}').columnTemplate(createElement),"
                        "    name: 'Available Datafiles',"
                        "    prop: 'title',"
                        "}]",
                    ),
                    frame_size=10,
                    hide_attribution=True,
                    id=self._revogrid_id,
                    readonly=True,
                    stretch=True,
                    source=(self._datafiles_name,),
                    theme="compact",
                    **kwargs,
                )
                if self._label:
                    self.label = self._label
                if "update_modelValue" not in kwargs:
                    self.update_modelValue = self._flush_state

                # Sets up some JavaScript event handlers when the component is mounted.
                with self:
                    client.ClientTriggers(
                        mounted=(
                            "window.grid_manager.add("
                            f"  '{self._revogrid_id}',"
                            f"  '{self._v_model}',"
                            f"  '{self._datafiles_name}',"
                            f"  '{self._v_model_name_in_state}'"
                            ")"
                        )
                    )

            with cast(
                vuetify.VSelect,
                InputField(
                    v_model=self._v_model,
                    classes="flex-0-1 nova-readonly",
                    clearable=True,
                    readonly=True,
                    type="select",
                    click_clear=self.reset,
                ),
            ):
                with vuetify.Template(raw_attrs=['v-slot:selection="{ item, index }"']):
                    vuetify.VChip("{{ item.title.split('/').reverse()[0] }}", v_if="index < 2")
                    html.Span(
                        f"(+{{{{ {self._v_model}.length - 2 }}}} others)", v_if="index === 2", classes="text-caption"
                    )

    def create_model(self) -> None:
        state = DataSelectorState()
        self._model = DataSelectorModel(state, self._directory, self._extensions, self._prefix)

    def create_viewmodel(self) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)

        self._vm = DataSelectorViewModel(self._model, binding)
        self._vm.state_bind.connect(self._state_name)
        self._vm.directories_bind.connect(self._directories_name)
        self._vm.datafiles_bind.connect(self._datafiles_name)
        self._vm.reset_bind.connect(self.reset)

        self._vm.update_view()

    def refresh_contents(self) -> None:
        self._vm.update_view(refresh_directories=True)

    def reset(self, _: Any = None) -> None:
        self._reset_state()
        self._reset_rv_grid()

    def set_state(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError(
            "The old DataSelector component has been renamed to NeutronDataSelector. Please import it from "
            "`nova.trame.view.components.ornl`."
        )

    async def _refresh_loop(self) -> None:
        if self._refresh_rate > 0:
            while True:
                await sleep(self._refresh_rate)

                self.refresh_contents()
                self.state.dirty(self._datafiles_name)
